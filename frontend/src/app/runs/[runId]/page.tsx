'use client';
import { use, useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import { useRun } from '@/hooks/useRun';
import { api } from '@/lib/api';
import {
  statusColor, statusDot, formatTime, formatDuration,
  logTypeColor, logTypeIcon, formatPayload, ALL_EVENT_TYPES
} from '@/lib/utils';
import type { ActivityLog } from '@/types/run';

// ─── Sub-components ───────────────────────────────────────────────────────────

function StatusHeader({ run }: { run: NonNullable<ReturnType<typeof useRun>['run']> }) {
  const nextWake = run.next_wakeup_at
    ? Math.max(0, Math.round((new Date(run.next_wakeup_at).getTime() - Date.now()) / 1000))
    : null;

  return (
    <div className="flex items-start justify-between mb-6">
      <div>
        <div className="flex items-center gap-3 mb-1">
          <span className={`inline-block w-3 h-3 rounded-full ${statusDot(run.status)}`} />
          <h1 className="text-xl font-bold text-white font-mono">{run.order_id}</h1>
          <span className={`px-2 py-0.5 rounded-md text-[11px] font-bold uppercase ${statusColor(run.status)}`}>
            {run.status}
          </span>
        </div>
        <p className="text-xs text-slate-500">Run ID: {run.id}</p>
      </div>
      <div className="text-right">
        {run.status === 'SLEEPING' && nextWake !== null && nextWake >= 0 && (
          <div className="bg-blue-950/40 border border-blue-800/40 rounded-lg px-3 py-2">
            <p className="text-[10px] text-blue-500 uppercase tracking-wide">Next Wake</p>
            <p className="text-blue-300 font-mono font-bold text-lg leading-none mt-0.5">
              {formatDuration(nextWake)}
            </p>
          </div>
        )}
        {run.paused && (
          <div className="bg-amber-950/40 border border-amber-800/40 rounded-lg px-3 py-2">
            <p className="text-amber-400 text-sm font-semibold">⏸ Paused</p>
          </div>
        )}
      </div>
    </div>
  );
}

function MemoryPanel({ memory }: { memory: string }) {
  return (
    <div className="bg-[#161b27] border border-white/5 rounded-xl p-4 mb-4">
      <div className="flex items-center gap-2 mb-3">
        <div className="w-5 h-5 rounded bg-violet-900/60 flex items-center justify-center">
          <span className="text-[10px]">🧠</span>
        </div>
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wide">Memory Summary</h3>
      </div>
      <p className="text-sm text-slate-300 leading-relaxed whitespace-pre-wrap">
        {memory || <span className="text-slate-600 italic">No memory yet — waiting for first agent run</span>}
      </p>
    </div>
  );
}

function FinalSummaryPanel({ summary }: { summary: string }) {
  return (
    <div className="bg-yellow-950/30 border border-yellow-700/40 rounded-xl p-4 mb-4">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-base">🏁</span>
        <h3 className="text-xs font-semibold text-yellow-400 uppercase tracking-wide">Final Summary</h3>
      </div>
      <div className="text-sm text-yellow-200/90 leading-relaxed whitespace-pre-wrap">
        {summary}
      </div>
    </div>
  );
}

function TimelineEntry({ entry }: { entry: ActivityLog }) {
  const [expanded, setExpanded] = useState(false);
  const colors = logTypeColor(entry.type);
  const icon = logTypeIcon(entry.type);
  const summary = formatPayload(entry.payload);

  // Show expanded detail on click
  const detail = JSON.stringify(entry.payload, null, 2);
  const isExpandable = detail.length > 50;

  return (
    <div className={`relative timeline-entry flex gap-3 mb-2`}>
      {/* Icon */}
      <div className={`relative z-10 flex-shrink-0 w-10 h-10 rounded-xl border flex items-center justify-center text-base ${colors}`}>
        {icon}
      </div>

      {/* Content */}
      <div
        className={`flex-1 min-w-0 border rounded-xl px-3 py-2.5 ${colors} ${isExpandable ? 'cursor-pointer' : ''}`}
        onClick={() => isExpandable && setExpanded(!expanded)}
      >
        <div className="flex items-center justify-between gap-2">
          <span className="text-[10px] font-bold uppercase tracking-wider opacity-60">{entry.type}</span>
          <span className="text-[10px] text-slate-500 font-mono shrink-0">{formatTime(entry.created_at)}</span>
        </div>
        <p className="text-xs mt-0.5 leading-relaxed truncate">{summary || 'No details'}</p>
        {expanded && (
          <pre className="text-[10px] mt-2 bg-black/20 rounded p-2 overflow-x-auto whitespace-pre-wrap text-slate-300">
            {detail}
          </pre>
        )}
      </div>
    </div>
  );
}

function Timeline({ timeline }: { timeline: ActivityLog[] }) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [timeline.length]);

  return (
    <div className="bg-[#161b27] border border-white/5 rounded-xl p-4 mb-4">
      <div className="flex items-center gap-2 mb-4">
        <div className="w-5 h-5 rounded bg-slate-800 flex items-center justify-center">
          <span className="text-[10px]">📜</span>
        </div>
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wide">Timeline</h3>
        <span className="ml-auto text-[10px] text-slate-600">{timeline.length} entries</span>
      </div>
      <div className="max-h-80 overflow-y-auto pr-1">
        {timeline.length === 0 ? (
          <p className="text-slate-600 text-xs text-center py-8">No events yet</p>
        ) : (
          timeline.map(entry => <TimelineEntry key={entry.id} entry={entry} />)
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}

function EventInjector({ runId, disabled }: { runId: string; disabled: boolean }) {
  const [eventType, setEventType] = useState('payment_confirmed');
  const [sending, setSending] = useState(false);
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const send = async () => {
    setSending(true);
    setFeedback(null);
    try {
      await api.events.send(runId, eventType);
      setFeedback({ type: 'success', message: `✓ Sent ${eventType}` });
      setTimeout(() => setFeedback(null), 4000);
    } catch (e) {
      setFeedback({ type: 'error', message: `⚠ ${(e as Error).message}` });
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="bg-[#161b27] border border-white/5 rounded-xl p-4 mb-4">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-base">📦</span>
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wide">Inject Event</h3>
      </div>
      <div className="flex gap-2">
        <select
          value={eventType}
          onChange={e => setEventType(e.target.value)}
          disabled={disabled}
          className="flex-1 bg-[#0f1117] border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-sky-500 transition-colors disabled:opacity-50"
        >
          {ALL_EVENT_TYPES.map(t => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
        <button
          onClick={send}
          disabled={disabled || sending}
          className="px-4 py-2 bg-sky-700 hover:bg-sky-600 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-colors"
        >
          {sending ? '...' : 'Send'}
        </button>
      </div>
      {feedback && (
        <div className={`mt-3 p-3 rounded-lg text-xs font-mono break-words leading-relaxed ${
          feedback.type === 'success'
            ? 'bg-emerald-950/50 border border-emerald-800/50 text-emerald-300'
            : 'bg-red-950/60 border border-red-800/60 text-red-300'
        }`}>
          {feedback.message}
        </div>
      )}
    </div>
  );
}

function InstructionBox({ runId, disabled }: { runId: string; disabled: boolean }) {
  const [text, setText] = useState('');
  const [sending, setSending] = useState(false);
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const send = async () => {
    if (!text.trim()) return;
    setSending(true);
    setFeedback(null);
    try {
      await api.instructions.add(runId, text.trim());
      setText('');
      setFeedback({ type: 'success', message: '✓ Instruction added' });
      setTimeout(() => setFeedback(null), 4000);
    } catch (e) {
      setFeedback({ type: 'error', message: `⚠ ${(e as Error).message}` });
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="bg-[#161b27] border border-white/5 rounded-xl p-4 mb-4">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-base">📋</span>
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wide">Add Instruction</h3>
      </div>
      <textarea
        value={text}
        onChange={e => setText(e.target.value)}
        disabled={disabled}
        placeholder="e.g. Escalate if shipment is delayed. Do not contact customer without review."
        rows={2}
        className="w-full bg-[#0f1117] border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-amber-500 transition-colors resize-none disabled:opacity-50"
      />
      {feedback && (
        <div className={`mt-2 p-2.5 rounded-lg text-xs font-mono break-words leading-relaxed ${
          feedback.type === 'success'
            ? 'bg-emerald-950/50 border border-emerald-800/50 text-emerald-300'
            : 'bg-red-950/60 border border-red-800/60 text-red-300'
        }`}>
          {feedback.message}
        </div>
      )}
      <button
        onClick={send}
        disabled={disabled || sending || !text.trim()}
        className="mt-2 w-full py-2 bg-amber-700/70 hover:bg-amber-600/80 disabled:opacity-50 text-amber-200 text-sm font-medium rounded-lg transition-colors"
      >
        {sending ? 'Adding...' : 'Add to Run Context'}
      </button>
    </div>
  );
}

function RunControls({ runId, status, onAction }: {
  runId: string;
  status: string;
  onAction: () => void;
}) {
  const [loading, setLoading] = useState<string | null>(null);

  const act = async (name: string, fn: () => Promise<unknown>) => {
    setLoading(name);
    try { await fn(); onAction(); }
    catch (e) { alert((e as Error).message); }
    finally { setLoading(null); }
  };

  const isTerminal = ['COMPLETED', 'TERMINATED', 'FAILED'].includes(status);
  const isPaused = status === 'PAUSED';

  return (
    <div className="bg-[#161b27] border border-white/5 rounded-xl p-4">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-base">🎛️</span>
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wide">Controls</h3>
      </div>
      <div className="flex gap-2 flex-wrap">
        {!isPaused && !isTerminal && (
          <button
            onClick={() => act('interrupt', () => api.controls.interrupt(runId))}
            disabled={loading !== null}
            className="flex-1 py-2 bg-amber-900/40 hover:bg-amber-800/60 border border-amber-700/40 text-amber-300 text-sm rounded-lg transition-colors disabled:opacity-50"
          >
            {loading === 'interrupt' ? '...' : '⏸ Pause'}
          </button>
        )}
        {isPaused && (
          <button
            onClick={() => act('resume', () => api.controls.resume(runId))}
            disabled={loading !== null}
            className="flex-1 py-2 bg-teal-900/40 hover:bg-teal-800/60 border border-teal-700/40 text-teal-300 text-sm rounded-lg transition-colors disabled:opacity-50"
          >
            {loading === 'resume' ? '...' : '▶ Resume'}
          </button>
        )}
        {!isTerminal && (
          <button
            onClick={() => {
              if (confirm('Terminate this workflow? This cannot be undone.')) {
                act('terminate', () => api.controls.terminate(runId));
              }
            }}
            disabled={loading !== null}
            className="flex-1 py-2 bg-red-950/40 hover:bg-red-900/60 border border-red-800/40 text-red-400 text-sm rounded-lg transition-colors disabled:opacity-50"
          >
            {loading === 'terminate' ? '...' : '🛑 Terminate'}
          </button>
        )}
        {isTerminal && (
          <p className="text-xs text-slate-500 py-2">
            Workflow has ended ({status})
          </p>
        )}
      </div>

      {/* Current instructions */}
      {/* Extra instructions list */}
    </div>
  );
}

function InstructionsList({ instructions }: { instructions: string[] }) {
  if (instructions.length === 0) return null;
  return (
    <div className="bg-amber-950/20 border border-amber-800/30 rounded-xl p-4 mb-4">
      <h3 className="text-xs font-semibold text-amber-500 uppercase tracking-wide mb-2">
        Active Instructions ({instructions.length})
      </h3>
      <ul className="space-y-1.5">
        {instructions.map((instr, i) => (
          <li key={i} className="flex items-start gap-2 text-xs text-amber-200/80">
            <span className="text-amber-600 mt-0.5 shrink-0">→</span>
            {instr}
          </li>
        ))}
      </ul>
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function RunDetailPage({ params }: { params: Promise<{ runId: string }> }) {
  const { runId } = use(params);
  const { run, loading, error, refresh } = useRun(runId);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full text-slate-500">
        <div className="flex items-center gap-3">
          <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          Loading run...
        </div>
      </div>
    );
  }

  if (error || !run) {
    return (
      <div className="p-8">
        <div className="bg-red-950/40 border border-red-800/50 text-red-400 rounded-xl p-4">
          ⚠️ {error || 'Run not found'}
        </div>
        <Link href="/runs" className="text-indigo-400 text-sm mt-4 inline-block hover:underline">
          ← Back to Runs
        </Link>
      </div>
    );
  }

  const isTerminal = ['COMPLETED', 'TERMINATED', 'FAILED'].includes(run.status);

  return (
    <div className="p-6 max-w-6xl mx-auto">
      {/* Back */}
      <Link href="/runs" className="inline-flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-300 transition-colors mb-5">
        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        All Runs
      </Link>

      <StatusHeader run={run} />

      <div className="grid grid-cols-3 gap-5">
        {/* Left column: timeline */}
        <div className="col-span-2 space-y-0">
          {run.final_summary && <FinalSummaryPanel summary={run.final_summary} />}
          <MemoryPanel memory={run.memory_summary} />
          <Timeline timeline={run.timeline} />
          {run.extra_instructions.length > 0 && (
            <InstructionsList instructions={run.extra_instructions} />
          )}
        </div>

        {/* Right column: controls */}
        <div className="space-y-0">
          <EventInjector runId={runId} disabled={isTerminal} />
          <InstructionBox runId={runId} disabled={isTerminal} />
          <RunControls runId={runId} status={run.status} onAction={refresh} />

          {/* Order context */}
          <div className="bg-[#161b27] border border-white/5 rounded-xl p-4 mt-4">
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">Order Context</h3>
            <dl className="space-y-1.5">
              {Object.entries(run.order_context).map(([k, v]) => (
                <div key={k} className="flex justify-between gap-2">
                  <dt className="text-[11px] text-slate-500 capitalize">{k.replace(/_/g, ' ')}</dt>
                  <dd className="text-[11px] text-slate-300 font-medium text-right">{String(v)}</dd>
                </div>
              ))}
            </dl>
          </div>
        </div>
      </div>
    </div>
  );
}
