"""
Persistence activity — syncs workflow state to PostgreSQL.
All datetimes are timezone-aware (UTC) to match DateTime(timezone=True) columns.
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
from temporalio import activity
from app.db.database import AsyncSessionLocal
from app.db.repositories.run_repository import RunRepository
from app.db.repositories.activity_repository import ActivityRepository

logger = logging.getLogger(__name__)


@activity.defn(name="persist_state")
async def persist_state(
    run_id: str,
    status: str,
    memory_summary: str,
    next_wakeup_in_seconds: Optional[int],
    final_summary: Optional[str] = None,
) -> None:
    """Update the runs table with current workflow state."""
    next_wakeup_at = None
    if next_wakeup_in_seconds is not None:
        next_wakeup_at = datetime.now(timezone.utc) + timedelta(
            seconds=next_wakeup_in_seconds
        )

    try:
        async with AsyncSessionLocal() as db:
            repo = RunRepository(db)
            await repo.update_status(
                run_id=run_id,
                status=status,
                memory_summary=memory_summary,
                next_wakeup_at=next_wakeup_at,
                final_summary=final_summary,
            )
        logger.debug(f"Persisted state for run {run_id}: status={status}")
    except Exception as e:
        logger.error(f"Failed to persist state for run {run_id} (status={status}): {e}", exc_info=True)
        raise  # Let Temporal retry this activity


@activity.defn(name="log_activity")
async def log_activity(run_id: str, log_type: str, payload: dict) -> None:
    """Append an entry to the activity log."""
    try:
        async with AsyncSessionLocal() as db:
            repo = ActivityRepository(db)
            await repo.append(run_id=run_id, log_type=log_type, payload=payload)
        logger.debug(f"Logged {log_type} for run {run_id}")
    except Exception as e:
        logger.error(f"Failed to log {log_type} for run {run_id}: {e}", exc_info=True)
        raise  # Let Temporal retry this activity
