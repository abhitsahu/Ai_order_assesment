export interface Supervisor {
  id: string;
  name: string;
  base_instruction: string;
  available_actions: string[];
  wake_aggressiveness: 'aggressive' | 'moderate' | 'conservative';
  default_wakeup_seconds: number;
  model_name: string;
  created_at: string;
}

export interface SupervisorCreate {
  name: string;
  base_instruction: string;
  available_actions: string[];
  wake_aggressiveness: string;
  default_wakeup_seconds: number;
  model_name: string;
}
