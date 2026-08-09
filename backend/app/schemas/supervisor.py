from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.core.constants import ALL_ACTIONS, WakeAggressiveness


class SupervisorCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    base_instruction: str = Field(..., min_length=10)
    available_actions: list[str] = Field(default_factory=lambda: ALL_ACTIONS)
    wake_aggressiveness: str = Field(default=WakeAggressiveness.MODERATE)
    default_wakeup_seconds: int = Field(default=30, ge=5, le=86400)
    model_name: str = Field(default="gemini-3.5-flash")


class SupervisorRead(BaseModel):
    id: str
    name: str
    base_instruction: str
    available_actions: list[str]
    wake_aggressiveness: str
    default_wakeup_seconds: int
    model_name: str
    created_at: datetime

    model_config = {"from_attributes": True}
