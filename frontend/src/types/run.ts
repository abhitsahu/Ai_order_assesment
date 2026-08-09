export type RunStatus =
  | 'CREATED'
  | 'RUNNING'
  | 'SLEEPING'
  | 'PAUSED'
  | 'COMPLETED'
  | 'TERMINATED'
  | 'FAILED';

export interface Run {
  id: string;
  order_id: string;
  supervisor_id: string;
  status: RunStatus;
  memory_summary: string;
  next_wakeup_at: string | null;
  paused: boolean;
  temporal_workflow_id: string | null;
  extra_instructions: string[];
  order_context: Record<string, unknown>;
  final_summary: string | null;
  created_at: string;
  completed_at: string | null;
}

export interface ActivityLog {
  id: string;
  run_id: string;
  type: 'EVENT' | 'AI_WAKE' | 'ACTION' | 'SLEEP' | 'INSTRUCTION' | 'FINAL_SUMMARY' | 'INTERRUPT' | 'RESUME' | 'TERMINATE' | 'SYSTEM';
  payload: Record<string, unknown>;
  created_at: string;
}

export interface RunDetail extends Run {
  timeline: ActivityLog[];
}

export interface RunCreate {
  order_id: string;
  supervisor_id: string;
  order_context: Record<string, unknown>;
}
