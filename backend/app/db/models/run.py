import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Text, Boolean, JSON, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base


class Run(Base):
    __tablename__ = "runs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    order_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    supervisor_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("supervisors.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), default="CREATED", index=True)
    memory_summary: Mapped[str] = mapped_column(Text, default="")
    next_wakeup_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    paused: Mapped[bool] = mapped_column(Boolean, default=False)
    temporal_workflow_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    extra_instructions: Mapped[list] = mapped_column(JSON, default=list)
    order_context: Mapped[dict] = mapped_column(JSON, default=dict)
    final_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
