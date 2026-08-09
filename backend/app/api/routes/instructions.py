from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.instruction import InstructionIn
from app.services.run_service import RunService

router = APIRouter(prefix="/runs", tags=["instructions"])
service = RunService()


@router.post("/{run_id}/instructions", status_code=200)
async def add_instruction(
    run_id: str, body: InstructionIn, db: AsyncSession = Depends(get_db)
):
    try:
        await service.add_instruction(db, run_id, body.text)
        return {"ok": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add instruction: {str(e)}")
