'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import type { Supervisor } from '@/types/supervisor';

const AGGRESSIVENESS_LABEL: Record<string, { label: string; color: string }> = {
  aggressive: { label: 'Aggressive', color: 'text-red-400 bg-red-900/30' },
  moderate: { label: 'Moderate', color: 'text-amber-400 bg-amber-900/30' },
  conservative: { label: 'Conservative', color: 'text-green-400 bg-green-900/30' },
};

function SupervisorCard({ supervisor, onDelete }: { supervisor: Supervisor; onDelete: () => void }) {
  const agg = AGGRESSIVENESS_LABEL[supervisor.wake_aggressiveness] || { label: supervisor.wake_aggressiveness, color: 'text-slate-400' };

  return (
    <div className="bg-[#161b27] border border-white/5 rounded-xl p-5 card-hover">
      <div className="flex items-start justify-between gap-3 mb-3">
        <div>
          <h3 className="font-semibold text-white">{supervisor.name}</h3>
          <p className="text-[11px] text-slate-500 mt-0.5">ID: {supervisor.id.slice(0, 12)}...</p>
        </div>
        <span className={`px-2 py-0.5 rounded-md text-[10px] font-bold uppercase ${agg.color}`}>
          {agg.label}
        </span>
      </div>
      <p className="text-xs text-slate-400 leading-relaxed line-clamp-3 mb-4">
        {supervisor.base_instruction}
      </p>
      <div className="flex items-center gap-3 flex-wrap mb-4">
        <div className="text-[10px] text-slate-500 bg-slate-800 rounded px-2 py-1">
          Sleep: {supervisor.default_wakeup_seconds}s
        </div>
        <div className="text-[10px] text-slate-500 bg-slate-800 rounded px-2 py-1">
          Model: {supervisor.model_name}
        </div>
        <div className="text-[10px] text-slate-500 bg-slate-800 rounded px-2 py-1">
          {supervisor.available_actions.length} actions
        </div>
      </div>
      <div className="flex gap-2">
        <Link
          href={`/runs/new?supervisor=${supervisor.id}`}
          className="flex-1 py-2 text-center text-xs bg-indigo-700/40 hover:bg-indigo-600/60 border border-indigo-700/40 text-indigo-300 rounded-lg transition-colors"
        >
          Start Run
        </Link>
        <button
          onClick={() => {
            if (confirm(`Delete "${supervisor.name}"?`)) {
              api.supervisors.delete(supervisor.id).then(onDelete).catch(e => alert(e.message));
            }
          }}
          className="px-3 py-2 text-xs bg-red-950/30 hover:bg-red-900/40 border border-red-800/30 text-red-400 rounded-lg transition-colors"
        >
          Delete
        </button>
      </div>
    </div>
  );
}

export default function SupervisorsPage() {
  const [supervisors, setSupervisors] = useState<Supervisor[]>([]);
  const [loading, setLoading] = useState(true);

  const load = () => {
    api.supervisors.list().then(setSupervisors).finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white">Supervisor Templates</h1>
          <p className="text-sm text-slate-500 mt-1">Configure AI supervisor behaviors and policies</p>
        </div>
        <Link
          href="/supervisors/create"
          className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-lg transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          New Template
        </Link>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-48 text-slate-500">
          <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mr-3" />
          Loading...
        </div>
      ) : supervisors.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-64 text-center">
          <p className="text-slate-400 mb-2">No supervisor templates yet</p>
          <Link href="/supervisors/create" className="text-indigo-400 text-sm hover:underline">
            Create your first template →
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4">
          {supervisors.map(s => (
            <SupervisorCard key={s.id} supervisor={s} onDelete={load} />
          ))}
        </div>
      )}
    </div>
  );
}
