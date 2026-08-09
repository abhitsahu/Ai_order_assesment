from typing import Any, Optional
from pydantic import BaseModel, Field


class AgentDecision(BaseModel):
    """Structured output from the Gemini agent."""
    reasoning: str = Field(default="", description="Agent's reasoning for its decision")
    actions: list[str] = Field(default_factory=list, description="List of action names to execute")
    action_params: dict[str, str] = Field(
        default_factory=dict,
        description="Parameters/messages for each action keyed by action name"
    )
    memory_summary: str = Field(
        default="", description="Updated compact memory summary"
    )
    next_wakeup_in_seconds: int = Field(
        default=30, ge=5, description="How many seconds to sleep before next check"
    )
    recommend_close: bool = Field(
        default=False, description="Agent suggests workflow can close (but workflow decides)"
    )


class AgentContext(BaseModel):
    """Context passed to the agent for decision making."""
    run_id: str
    order_id: str
    supervisor_name: str
    base_instruction: str
    extra_instructions: list[str]
    available_actions: list[str]
    order_context: dict[str, Any]
    memory_summary: str
    recent_timeline: list[dict]
    trigger_reason: str  # "initial_start" | "important_signal:<event>" | "timer" | "resume"
    wake_aggressiveness: str
    default_wakeup_seconds: int
