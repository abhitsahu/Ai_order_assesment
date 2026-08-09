from typing import Any
from pydantic import BaseModel, Field
from app.core.constants import ALL_EVENT_TYPES


class EventIn(BaseModel):
    type: str = Field(..., description=f"One of: {ALL_EVENT_TYPES}")
    payload: dict[str, Any] = Field(default_factory=dict)
