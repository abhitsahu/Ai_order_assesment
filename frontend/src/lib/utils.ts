import type { RunStatus } from '@/types/run';

export function cn(...classes: (string | undefined | false | null)[]): string {
  return classes.filter(Boolean).join(' ');
}

export function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  });
}

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds}s`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
  return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
}

export function statusColor(status: RunStatus): string {
  const map: Record<RunStatus, string> = {
    CREATED: 'text-slate-400 bg-slate-800',
    RUNNING: 'text-emerald-400 bg-emerald-900/40',
    SLEEPING: 'text-blue-400 bg-blue-900/40',
    PAUSED: 'text-amber-400 bg-amber-900/40',
    COMPLETED: 'text-purple-400 bg-purple-900/40',
    TERMINATED: 'text-red-400 bg-red-900/40',
    FAILED: 'text-red-500 bg-red-900/60',
  };
  return map[status] || 'text-slate-400 bg-slate-800';
}

export function statusDot(status: RunStatus): string {
  const map: Record<RunStatus, string> = {
    CREATED: 'bg-slate-400',
    RUNNING: 'bg-emerald-400 animate-pulse',
    SLEEPING: 'bg-blue-400',
    PAUSED: 'bg-amber-400',
    COMPLETED: 'bg-purple-400',
    TERMINATED: 'bg-red-400',
    FAILED: 'bg-red-500',
  };
  return map[status] || 'bg-slate-400';
}

export function logTypeColor(type: string): string {
  const map: Record<string, string> = {
    EVENT: 'text-sky-400 border-sky-800 bg-sky-950/50',
    AI_WAKE: 'text-violet-400 border-violet-800 bg-violet-950/50',
    ACTION: 'text-emerald-400 border-emerald-800 bg-emerald-950/50',
    SLEEP: 'text-slate-400 border-slate-700 bg-slate-900/50',
    INSTRUCTION: 'text-amber-400 border-amber-800 bg-amber-950/50',
    FINAL_SUMMARY: 'text-yellow-300 border-yellow-700 bg-yellow-950/60',
    INTERRUPT: 'text-orange-400 border-orange-800 bg-orange-950/50',
    RESUME: 'text-teal-400 border-teal-800 bg-teal-950/50',
    TERMINATE: 'text-red-400 border-red-800 bg-red-950/50',
    SYSTEM: 'text-slate-500 border-slate-800 bg-slate-950/30',
  };
  return map[type] || 'text-slate-400 border-slate-700';
}

export function logTypeIcon(type: string): string {
  const map: Record<string, string> = {
    EVENT: '📦',
    AI_WAKE: '🤖',
    ACTION: '⚡',
    SLEEP: '💤',
    INSTRUCTION: '📋',
    FINAL_SUMMARY: '🏁',
    INTERRUPT: '⏸',
    RESUME: '▶️',
    TERMINATE: '🛑',
    SYSTEM: '⚙️',
  };
  return map[type] || '•';
}

export function formatPayload(payload: Record<string, unknown>): string {
  const skip = ['simulated', 'run_id'];
  const parts = Object.entries(payload)
    .filter(([k]) => !skip.includes(k))
    .map(([k, v]) => {
      if (typeof v === 'string' && v.length > 80) {
        return `${k}: ${v.slice(0, 80)}...`;
      }
      return `${k}: ${v}`;
    });
  return parts.join(' · ');
}

export const ALL_EVENT_TYPES = [
  'order_created',
  'payment_confirmed',
  'payment_failed',
  'shipment_created',
  'shipment_delayed',
  'delivered',
  'refund_requested',
  'customer_message_received',
  'no_update_for_n_hours',
];

export const ALL_ACTIONS = [
  'message_fulfillment_team',
  'message_payments_team',
  'message_logistics_team',
  'message_customer',
  'create_internal_note',
];
