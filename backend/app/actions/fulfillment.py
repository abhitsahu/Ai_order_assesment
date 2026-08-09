"""
Business action: message_fulfillment_team
Writes an action record to the activity log.
"""
from app.core.constants import ActionName, LogType


async def message_fulfillment_team(run_id: str, message: str, db) -> dict:
    from app.db.repositories.activity_repository import ActivityRepository
    repo = ActivityRepository(db)
    entry = await repo.append(
        run_id=run_id,
        log_type=LogType.ACTION,
        payload={
            "action_name": ActionName.MESSAGE_FULFILLMENT_TEAM,
            "message": message,
            "team": "fulfillment",
            "simulated": True,
        },
    )
    return {"action": ActionName.MESSAGE_FULFILLMENT_TEAM, "id": entry.id}
