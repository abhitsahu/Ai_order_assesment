import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, JSON, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base


class Supervisor(Base):
    __tablename__ = "supervisors"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    base_instruction: Mapped[str] = mapped_column(Text, nullable=False)
    available_actions: Mapped[list] = mapped_column(JSON, default=list)
    wake_aggressiveness: Mapped[str] = mapped_column(String(20), default="moderate")
    default_wakeup_seconds: Mapped[int] = mapped_column(Integer, default=30)
    model_name: Mapped[str] = mapped_column(String(100), default="gemini-3.5-flash")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
