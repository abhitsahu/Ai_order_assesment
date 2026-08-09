from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field


class RunCreate(BaseModel):
    order_id: str = Field(..., min_length=1)
    supervisor_id: str
    order_context: dict[str, Any] = Field(default_factory=dict)


class ActivityLogRead(BaseModel):
    id: str
    run_id: str
    type: str
    payload: dict
    created_at: datetime

    model_config = {"from_attributes": True}


class RunRead(BaseModel):
    id: str
    order_id: str
    supervisor_id: str
    status: str
    memory_summary: str
    next_wakeup_at: Optional[datetime]
    paused: bool
    temporal_workflow_id: Optional[str]
    extra_instructions: list[str]
    order_context: dict
    final_summary: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True}


class RunDetail(RunRead):
    timeline: list[ActivityLogRead] = Field(default_factory=list)
