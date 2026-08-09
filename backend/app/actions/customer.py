"""
Business action: message_customer
"""
from app.core.constants import ActionName, LogType


async def message_customer(run_id: str, message: str, db) -> dict:
    from app.db.repositories.activity_repository import ActivityRepository
    repo = ActivityRepository(db)
    entry = await repo.append(
        run_id=run_id,
        log_type=LogType.ACTION,
        payload={
            "action_name": ActionName.MESSAGE_CUSTOMER,
            "message": message,
            "channel": "email",
            "simulated": True,
        },
    )
    return {"action": ActionName.MESSAGE_CUSTOMER, "id": entry.id}
