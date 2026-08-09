"""
Business action: message_payments_team
"""
from app.core.constants import ActionName, LogType


async def message_payments_team(run_id: str, message: str, db) -> dict:
    from app.db.repositories.activity_repository import ActivityRepository
    repo = ActivityRepository(db)
    entry = await repo.append(
        run_id=run_id,
        log_type=LogType.ACTION,
        payload={
            "action_name": ActionName.MESSAGE_PAYMENTS_TEAM,
            "message": message,
            "team": "payments",
            "simulated": True,
        },
    )
    return {"action": ActionName.MESSAGE_PAYMENTS_TEAM, "id": entry.id}
