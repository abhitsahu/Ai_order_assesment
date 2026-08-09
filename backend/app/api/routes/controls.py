from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from temporalio.service import RPCError
from app.db.database import get_db
from app.services.run_service import RunService

router = APIRouter(prefix="/runs", tags=["controls"])
service = RunService()


@router.post("/{run_id}/interrupt", status_code=200)
async def interrupt_run(run_id: str, db: AsyncSession = Depends(get_db)):
    try:
        await service.interrupt(db, run_id)
        return {"ok": True, "status": "PAUSED"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RPCError as e:
        # Workflow already gone — DB was still updated, treat as success
        return {"ok": True, "status": "PAUSED", "warning": str(e)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{run_id}/resume", status_code=200)
async def resume_run(run_id: str, db: AsyncSession = Depends(get_db)):
    try:
        await service.resume(db, run_id)
        return {"ok": True, "status": "RUNNING"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RPCError as e:
        return {"ok": True, "status": "RUNNING", "warning": str(e)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{run_id}/terminate", status_code=200)
async def terminate_run(run_id: str, db: AsyncSession = Depends(get_db)):
    try:
        await service.terminate(db, run_id)
        return {"ok": True, "status": "TERMINATED"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RPCError as e:
        # Workflow not found — it's already gone; DB update still happened
        return {"ok": True, "status": "TERMINATED", "warning": str(e)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
