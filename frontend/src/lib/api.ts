const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

async function request<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Request failed: ${res.status}`);
  }
  // 204 No Content
  if (res.status === 204) return undefined as T;
  return res.json();
}

// ─── Supervisors ────────────────────────────────────────────────────────────

import type { Supervisor, SupervisorCreate } from '@/types/supervisor';
import type { Run, RunCreate, RunDetail } from '@/types/run';

export const api = {
  supervisors: {
    list: () => request<Supervisor[]>('/supervisors'),
    get: (id: string) => request<Supervisor>(`/supervisors/${id}`),
    create: (data: SupervisorCreate) =>
      request<Supervisor>('/supervisors', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    delete: (id: string) =>
      request<void>(`/supervisors/${id}`, { method: 'DELETE' }),
  },

  runs: {
    list: () => request<Run[]>('/runs'),
    get: (id: string) => request<RunDetail>(`/runs/${id}`),
    create: (data: RunCreate) =>
      request<Run>('/runs', { method: 'POST', body: JSON.stringify(data) }),
  },

  events: {
    send: (runId: string, type: string, payload: Record<string, unknown> = {}) =>
      request<{ ok: boolean }>(`/runs/${runId}/events`, {
        method: 'POST',
        body: JSON.stringify({ type, payload }),
      }),
  },

  instructions: {
    add: (runId: string, text: string) =>
      request<{ ok: boolean }>(`/runs/${runId}/instructions`, {
        method: 'POST',
        body: JSON.stringify({ text }),
      }),
  },

  controls: {
    interrupt: (runId: string) =>
      request<{ ok: boolean }>(`/runs/${runId}/interrupt`, { method: 'POST' }),
    resume: (runId: string) =>
      request<{ ok: boolean }>(`/runs/${runId}/resume`, { method: 'POST' }),
    terminate: (runId: string) =>
      request<{ ok: boolean }>(`/runs/${runId}/terminate`, { method: 'POST' }),
  },
};
