import uuid
from datetime import datetime, timezone
from sqlalchemy import String, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base


class ActivityLog(Base):
    __tablename__ = "activity_log"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("runs.id"), nullable=False, index=True
    )
    type: Mapped[str] = mapped_column(
        String(30), nullable=False
    )  # EVENT|AI_WAKE|ACTION|SLEEP|INSTRUCTION|FINAL_SUMMARY|INTERRUPT|RESUME|TERMINATE|SYSTEM
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
