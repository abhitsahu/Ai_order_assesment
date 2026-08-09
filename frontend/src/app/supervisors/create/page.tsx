'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { ALL_ACTIONS } from '@/lib/utils';

export default function CreateSupervisorPage() {
  const router = useRouter();
  const [form, setForm] = useState({
    name: '',
    base_instruction: '',
    available_actions: ALL_ACTIONS,
    wake_aggressiveness: 'moderate',
    default_wakeup_seconds: 30,
    model_name: 'gemini-3.5-flash',
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const toggleAction = (action: string) => {
    setForm(prev => ({
      ...prev,
      available_actions: prev.available_actions.includes(action)
        ? prev.available_actions.filter(a => a !== action)
        : [...prev.available_actions, action],
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');
    try {
      await api.supervisors.create(form);
      router.push('/supervisors');
    } catch (e) {
      setError((e as Error).message);
      setSubmitting(false);
    }
  };

  return (
    <div className="p-8 max-w-2xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white">Create Supervisor Template</h1>
        <p className="text-sm text-slate-500 mt-1">Define how the AI agent will behave for orders using this template</p>
      </div>

      {error && (
        <div className="bg-red-950/40 border border-red-800/50 text-red-400 rounded-xl p-4 mb-6 text-sm">
          ⚠️ {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Name */}
        <div className="bg-[#161b27] border border-white/5 rounded-xl p-5">
          <label className="block text-sm font-medium text-slate-300 mb-2">Name *</label>
          <input
            type="text"
            value={form.name}
            onChange={e => setForm(p => ({ ...p, name: e.target.value }))}
            placeholder="e.g. High-Value Order Ops"
            className="w-full bg-[#0f1117] border border-white/10 rounded-lg px-3 py-2.5 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-indigo-500 transition-colors"
            required
          />
        </div>

        {/* Base Instruction */}
        <div className="bg-[#161b27] border border-white/5 rounded-xl p-5">
          <label className="block text-sm font-medium text-slate-300 mb-2">Base Instruction *</label>
          <textarea
            value={form.base_instruction}
            onChange={e => setForm(p => ({ ...p, base_instruction: e.target.value }))}
            placeholder="You are an order operations supervisor. Monitor order lifecycle events and take appropriate actions..."
            rows={5}
            className="w-full bg-[#0f1117] border border-white/10 rounded-lg px-3 py-2.5 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-indigo-500 transition-colors resize-none"
            required
          />
        </div>

        {/* Available Actions */}
        <div className="bg-[#161b27] border border-white/5 rounded-xl p-5">
          <label className="block text-sm font-medium text-slate-300 mb-3">Available Actions</label>
          <div className="space-y-2">
            {ALL_ACTIONS.map(action => (
              <label key={action} className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={form.available_actions.includes(action)}
                  onChange={() => toggleAction(action)}
                  className="accent-indigo-500 w-4 h-4"
                />
                <span className="text-sm text-slate-300 font-mono">{action}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Wake Aggressiveness */}
        <div className="bg-[#161b27] border border-white/5 rounded-xl p-5">
          <label className="block text-sm font-medium text-slate-300 mb-3">Wake Aggressiveness</label>
          <div className="grid grid-cols-3 gap-2">
            {(['conservative', 'moderate', 'aggressive'] as const).map(level => (
              <button
                key={level}
                type="button"
                onClick={() => setForm(p => ({ ...p, wake_aggressiveness: level }))}
                className={`py-2 px-3 rounded-lg text-xs font-semibold capitalize border transition-all ${form.wake_aggressiveness === level
                    ? level === 'aggressive'
                      ? 'bg-red-900/40 border-red-600/60 text-red-300'
                      : level === 'moderate'
                        ? 'bg-amber-900/40 border-amber-600/60 text-amber-300'
                        : 'bg-green-900/40 border-green-600/60 text-green-300'
                    : 'border-white/10 text-slate-500 hover:border-white/20'
                  }`}
              >
                {level}
              </button>
            ))}
          </div>
          <p className="text-[11px] text-slate-600 mt-2">
            {form.wake_aggressiveness === 'aggressive' && 'Agent wakes on every event'}
            {form.wake_aggressiveness === 'moderate' && 'Agent wakes on important events (delays, failures, refunds)'}
            {form.wake_aggressiveness === 'conservative' && 'Agent only wakes on critical events (payment failure, refund)'}
          </p>
        </div>

        {/* Sleep Duration */}
        <div className="bg-[#161b27] border border-white/5 rounded-xl p-5">
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Default Sleep Duration: <span className="text-indigo-400">{form.default_wakeup_seconds}s</span>
          </label>
          <input
            type="range"
            min={10}
            max={300}
            step={5}
            value={form.default_wakeup_seconds}
            onChange={e => setForm(p => ({ ...p, default_wakeup_seconds: Number(e.target.value) }))}
            className="w-full accent-indigo-500"
          />
          <div className="flex justify-between text-[10px] text-slate-600 mt-1">
            <span>10s (fast)</span>
            <span>5m (slow)</span>
          </div>
        </div>

        {/* Submit */}
        <div className="flex gap-3">
          <button
            type="submit"
            disabled={submitting}
            className="flex-1 py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-medium rounded-xl transition-colors"
          >
            {submitting ? 'Creating...' : 'Create Template'}
          </button>
          <a href="/supervisors" className="px-5 py-3 text-sm text-slate-400 hover:text-slate-200 transition-colors">
            Cancel
          </a>
        </div>
      </form>
    </div>
  );
}
