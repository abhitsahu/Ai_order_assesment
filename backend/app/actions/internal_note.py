"""
Business action: create_internal_note
"""
from app.core.constants import ActionName, LogType


async def create_internal_note(run_id: str, message: str, db) -> dict:
    from app.db.repositories.activity_repository import ActivityRepository
    repo = ActivityRepository(db)
    entry = await repo.append(
        run_id=run_id,
        log_type=LogType.ACTION,
        payload={
            "action_name": ActionName.CREATE_INTERNAL_NOTE,
            "note": message,
            "simulated": True,
        },
    )
    return {"action": ActionName.CREATE_INTERNAL_NOTE, "id": entry.id}
