"""
Business action: message_logistics_team
"""
from app.core.constants import ActionName, LogType


async def message_logistics_team(run_id: str, message: str, db) -> dict:
    from app.db.repositories.activity_repository import ActivityRepository
    repo = ActivityRepository(db)
    entry = await repo.append(
        run_id=run_id,
        log_type=LogType.ACTION,
        payload={
            "action_name": ActionName.MESSAGE_LOGISTICS_TEAM,
            "message": message,
            "team": "logistics",
            "simulated": True,
        },
    )
    return {"action": ActionName.MESSAGE_LOGISTICS_TEAM, "id": entry.id}
