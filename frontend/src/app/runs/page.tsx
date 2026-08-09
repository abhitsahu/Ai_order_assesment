'use client';
import Link from 'next/link';
import { useRuns } from '@/hooks/useRuns';
import { statusColor, statusDot, formatDate, formatDuration } from '@/lib/utils';
import type { Run } from '@/types/run';

function RunRow({ run }: { run: Run }) {
  const isActive = run.status === 'RUNNING' || run.status === 'SLEEPING';
  const nextWake = run.next_wakeup_at
    ? Math.max(0, Math.round((new Date(run.next_wakeup_at).getTime() - Date.now()) / 1000))
    : null;

  return (
    <Link href={`/runs/${run.id}`}>
      <div className="group flex items-center gap-4 px-5 py-4 bg-[#161b27] border border-white/5 rounded-xl hover:border-indigo-700/40 hover:bg-[#1a2035] transition-all duration-150 cursor-pointer card-hover">
        {/* Status indicator */}
        <div className="flex-shrink-0">
          <span className={`inline-block w-2.5 h-2.5 rounded-full ${statusDot(run.status)}`} />
        </div>

        {/* Order ID */}
        <div className="w-32 shrink-0">
          <p className="text-sm font-mono font-semibold text-white">{run.order_id}</p>
          <p className="text-[11px] text-slate-500 mt-0.5">{run.id.slice(0, 8)}...</p>
        </div>

        {/* Status badge */}
        <div className="w-28 shrink-0">
          <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-semibold uppercase tracking-wide ${statusColor(run.status)}`}>
            {run.status}
          </span>
        </div>

        {/* Memory snippet */}
        <div className="flex-1 min-w-0">
          <p className="text-xs text-slate-400 truncate">
            {run.memory_summary || 'No memory yet'}
          </p>
        </div>

        {/* Next wake / timing */}
        <div className="w-32 shrink-0 text-right">
          {run.status === 'SLEEPING' && nextWake !== null && nextWake >= 0 ? (
            <p className="text-xs text-blue-400">
              Wakes in {formatDuration(nextWake)}
            </p>
          ) : run.completed_at ? (
            <p className="text-xs text-slate-500">Done {formatDate(run.completed_at)}</p>
          ) : (
            <p className="text-xs text-slate-500">{formatDate(run.created_at)}</p>
          )}
        </div>

        {/* Arrow */}
        <svg className="w-4 h-4 text-slate-600 group-hover:text-indigo-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </div>
    </Link>
  );
}

function StatsBar({ runs }: { runs: Run[] }) {
  const active = runs.filter(r => ['RUNNING', 'SLEEPING', 'PAUSED'].includes(r.status)).length;
  const completed = runs.filter(r => r.status === 'COMPLETED').length;
  const terminated = runs.filter(r => r.status === 'TERMINATED').length;

  return (
    <div className="grid grid-cols-4 gap-3 mb-6">
      {[
        { label: 'Total Runs', value: runs.length, color: 'text-white' },
        { label: 'Active', value: active, color: 'text-emerald-400' },
        { label: 'Completed', value: completed, color: 'text-purple-400' },
        { label: 'Terminated', value: terminated, color: 'text-red-400' },
      ].map(stat => (
        <div key={stat.label} className="bg-[#161b27] border border-white/5 rounded-xl p-4">
          <p className={`text-2xl font-bold ${stat.color}`}>{stat.value}</p>
          <p className="text-xs text-slate-500 mt-1">{stat.label}</p>
        </div>
      ))}
    </div>
  );
}

export default function RunsPage() {
  const { runs, loading, error } = useRuns();

  const active = runs.filter(r => ['RUNNING', 'SLEEPING', 'PAUSED', 'CREATED'].includes(r.status));
  const done = runs.filter(r => ['COMPLETED', 'TERMINATED', 'FAILED'].includes(r.status));

  return (
    <div className="p-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white">Order Runs</h1>
          <p className="text-sm text-slate-500 mt-1">Monitor active and completed order workflows</p>
        </div>
        <Link
          href="/runs/new"
          className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-lg transition-colors shadow-lg shadow-indigo-900/30"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          New Run
        </Link>
      </div>

      {loading && (
        <div className="flex items-center justify-center h-48 text-slate-500">
          <div className="flex items-center gap-3">
            <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            Loading runs...
          </div>
        </div>
      )}

      {error && (
        <div className="bg-red-950/40 border border-red-800/50 text-red-400 rounded-xl p-4 mb-6">
          ⚠️ {error} — make sure the backend is running on port 8000
        </div>
      )}

      {!loading && !error && (
        <>
          <StatsBar runs={runs} />

          {/* Active runs */}
          {active.length > 0 && (
            <div className="mb-6">
              <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-3">
                Active ({active.length})
              </h2>
              <div className="space-y-2">
                {active.map(run => <RunRow key={run.id} run={run} />)}
              </div>
            </div>
          )}

          {/* Completed runs */}
          {done.length > 0 && (
            <div>
              <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-3">
                Completed ({done.length})
              </h2>
              <div className="space-y-2">
                {done.map(run => <RunRow key={run.id} run={run} />)}
              </div>
            </div>
          )}

          {runs.length === 0 && (
            <div className="flex flex-col items-center justify-center h-64 text-center">
              <div className="w-16 h-16 rounded-2xl bg-[#161b27] border border-white/5 flex items-center justify-center mb-4">
                <svg className="w-7 h-7 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <p className="text-slate-400 font-medium">No runs yet</p>
              <p className="text-slate-600 text-sm mt-1">Start a new order run to begin supervision</p>
              <Link
                href="/runs/new"
                className="mt-4 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-lg transition-colors"
              >
                Start First Run
              </Link>
            </div>
          )}
        </>
      )}
    </div>
  );
}
