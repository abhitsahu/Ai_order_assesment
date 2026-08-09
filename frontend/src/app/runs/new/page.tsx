'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { ALL_ACTIONS } from '@/lib/utils';
import type { Supervisor } from '@/types/supervisor';

// Inline supervisor selector + run creation form
export default function NewRunPage() {
  const router = useRouter();
  const [supervisors, setSupervisors] = useState<Supervisor[]>([]);
  const [loadingSupervisors, setLoadingSupervisors] = useState(true);
  const [selectedSupervisor, setSelectedSupervisor] = useState('');
  const [orderId, setOrderId] = useState('');
  const [orderContext, setOrderContext] = useState<Record<string, string>>({
    customer_name: '',
    product: '',
    amount: '',
    priority: 'standard',
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  // Load supervisors
  useState(() => {
    api.supervisors.list().then(s => {
      setSupervisors(s);
      if (s.length > 0) setSelectedSupervisor(s[0].id);
    }).finally(() => setLoadingSupervisors(false));
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!orderId.trim() || !selectedSupervisor) {
      setError('Order ID and supervisor are required');
      return;
    }
    setSubmitting(true);
    setError('');
    try {
      const run = await api.runs.create({
        order_id: orderId.trim(),
        supervisor_id: selectedSupervisor,
        order_context: Object.fromEntries(
          Object.entries(orderContext).filter(([, v]) => v !== '')
        ),
      });
      router.push(`/runs/${run.id}`);
    } catch (e) {
      setError((e as Error).message);
      setSubmitting(false);
    }
  };

  const supervisor = supervisors.find(s => s.id === selectedSupervisor);

  return (
    <div className="p-8 max-w-2xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white">Start New Run</h1>
        <p className="text-sm text-slate-500 mt-1">Launch a Temporal workflow to supervise an order</p>
      </div>

      {error && (
        <div className="bg-red-950/40 border border-red-800/50 text-red-400 rounded-xl p-4 mb-6 text-sm">
          ⚠️ {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Order ID */}
        <div className="bg-[#161b27] border border-white/5 rounded-xl p-5">
          <label className="block text-sm font-medium text-slate-300 mb-3">Order ID *</label>
          <input
            type="text"
            value={orderId}
            onChange={e => setOrderId(e.target.value)}
            placeholder="e.g. ORD-2026-001"
            className="w-full bg-[#0f1117] border border-white/10 rounded-lg px-3 py-2.5 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-indigo-500 transition-colors font-mono"
            required
          />
        </div>

        {/* Supervisor */}
        <div className="bg-[#161b27] border border-white/5 rounded-xl p-5">
          <label className="block text-sm font-medium text-slate-300 mb-3">Supervisor Template *</label>
          {loadingSupervisors ? (
            <div className="text-slate-500 text-sm">Loading supervisors...</div>
          ) : supervisors.length === 0 ? (
            <div className="text-amber-400 text-sm">
              No supervisors found. <a href="/supervisors/create" className="underline">Create one first</a>.
            </div>
          ) : (
            <div className="space-y-2">
              {supervisors.map(s => (
                <label
                  key={s.id}
                  className={`flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-all ${
                    selectedSupervisor === s.id
                      ? 'border-indigo-600/60 bg-indigo-900/20'
                      : 'border-white/5 hover:border-white/10'
                  }`}
                >
                  <input
                    type="radio"
                    name="supervisor"
                    value={s.id}
                    checked={selectedSupervisor === s.id}
                    onChange={() => setSelectedSupervisor(s.id)}
                    className="mt-0.5 accent-indigo-500"
                  />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-white">{s.name}</p>
                    <p className="text-xs text-slate-500 mt-0.5 line-clamp-2">{s.base_instruction}</p>
                    <div className="flex items-center gap-3 mt-1.5">
                      <span className="text-[10px] text-slate-600">
                        Wake: {s.wake_aggressiveness}
                      </span>
                      <span className="text-[10px] text-slate-600">
                        Sleep: {s.default_wakeup_seconds}s
                      </span>
                    </div>
                  </div>
                </label>
              ))}
            </div>
          )}
        </div>

        {/* Order Context */}
        <div className="bg-[#161b27] border border-white/5 rounded-xl p-5">
          <label className="block text-sm font-medium text-slate-300 mb-3">Order Context</label>
          <div className="grid grid-cols-2 gap-3">
            {['customer_name', 'product', 'amount', 'priority'].map(field => (
              <div key={field}>
                <label className="block text-[11px] text-slate-500 mb-1 capitalize">
                  {field.replace('_', ' ')}
                </label>
                {field === 'priority' ? (
                  <select
                    value={orderContext[field]}
                    onChange={e => setOrderContext(prev => ({ ...prev, [field]: e.target.value }))}
                    className="w-full bg-[#0f1117] border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500 transition-colors"
                  >
                    <option value="standard">Standard</option>
                    <option value="express">Express</option>
                    <option value="vip">VIP</option>
                  </select>
                ) : (
                  <input
                    type="text"
                    value={orderContext[field]}
                    onChange={e => setOrderContext(prev => ({ ...prev, [field]: e.target.value }))}
                    placeholder={field === 'amount' ? '$0.00' : ''}
                    className="w-full bg-[#0f1117] border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-indigo-500 transition-colors"
                  />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Submit */}
        <div className="flex items-center gap-3">
          <button
            type="submit"
            disabled={submitting || !orderId || !selectedSupervisor}
            className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium rounded-xl transition-colors shadow-lg shadow-indigo-900/30"
          >
            {submitting ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Starting Workflow...
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                Launch Supervisor
              </>
            )}
          </button>
          <a href="/runs" className="px-4 py-3 text-sm text-slate-400 hover:text-slate-200 transition-colors">
            Cancel
          </a>
        </div>
      </form>
    </div>
  );
}
