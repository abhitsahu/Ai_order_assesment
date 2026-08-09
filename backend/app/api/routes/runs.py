from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.run import RunCreate, RunRead, RunDetail
from app.services.run_service import RunService

router = APIRouter(prefix="/runs", tags=["runs"])
service = RunService()


@router.post("", response_model=RunRead, status_code=201)
async def create_run(data: RunCreate, db: AsyncSession = Depends(get_db)):
    try:
        run = await service.create_run(db, data)
        return run
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start workflow: {str(e)}")


@router.get("", response_model=list[RunRead])
async def list_runs(db: AsyncSession = Depends(get_db)):
    try:
        return await service.list_runs(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list runs: {str(e)}")


@router.get("/{run_id}", response_model=RunDetail)
async def get_run(run_id: str, db: AsyncSession = Depends(get_db)):
    try:
        detail = await service.get_run_detail(db, run_id)
        if not detail:
            raise HTTPException(status_code=404, detail="Run not found")
        return detail
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch run: {str(e)}")
