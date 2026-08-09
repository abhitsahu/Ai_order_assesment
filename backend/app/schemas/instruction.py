from pydantic import BaseModel, Field


class InstructionIn(BaseModel):
    text: str = Field(..., min_length=1, description="Run-specific instruction text")
