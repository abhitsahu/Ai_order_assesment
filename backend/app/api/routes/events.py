from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.event import EventIn
from app.services.run_service import RunService

router = APIRouter(prefix="/runs", tags=["events"])
service = RunService()


@router.post("/{run_id}/events", status_code=200)
async def send_event(
    run_id: str, event: EventIn, db: AsyncSession = Depends(get_db)
):
    try:
        await service.send_event(
            db, run_id, {"type": event.type, "payload": event.payload}
        )
        return {"ok": True, "event_type": event.type}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send event: {str(e)}")
