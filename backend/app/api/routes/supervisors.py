from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.supervisor import SupervisorCreate, SupervisorRead
from app.services.supervisor_service import SupervisorService

router = APIRouter(prefix="/supervisors", tags=["supervisors"])
service = SupervisorService()


@router.post("", response_model=SupervisorRead, status_code=201)
async def create_supervisor(
    data: SupervisorCreate, db: AsyncSession = Depends(get_db)
):
    try:
        return await service.create(db, data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create supervisor: {str(e)}")


@router.get("", response_model=list[SupervisorRead])
async def list_supervisors(db: AsyncSession = Depends(get_db)):
    try:
        return await service.list_all(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list supervisors: {str(e)}")


@router.get("/{supervisor_id}", response_model=SupervisorRead)
async def get_supervisor(supervisor_id: str, db: AsyncSession = Depends(get_db)):
    try:
        supervisor = await service.get(db, supervisor_id)
        if not supervisor:
            raise HTTPException(status_code=404, detail="Supervisor not found")
        return supervisor
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch supervisor: {str(e)}")


@router.delete("/{supervisor_id}", status_code=204)
async def delete_supervisor(supervisor_id: str, db: AsyncSession = Depends(get_db)):
    try:
        deleted = await service.delete(db, supervisor_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Supervisor not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete supervisor: {str(e)}")
