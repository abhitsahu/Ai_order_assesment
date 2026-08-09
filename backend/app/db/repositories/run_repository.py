from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.run import Run


class RunRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> Run:
        run = Run(**data)
        self.db.add(run)
        await self.db.commit()
        await self.db.refresh(run)
        return run

    async def get_by_id(self, run_id: str) -> Optional[Run]:
        result = await self.db.execute(
            select(Run).where(Run.id == run_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Run]:
        result = await self.db.execute(
            select(Run).order_by(Run.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_by_status(self, status: str) -> list[Run]:
        result = await self.db.execute(
            select(Run).where(Run.status == status).order_by(Run.created_at.desc())
        )
        return list(result.scalars().all())

    async def update_status(
        self,
        run_id: str,
        status: str,
        memory_summary: Optional[str] = None,
        next_wakeup_at: Optional[datetime] = None,
        paused: Optional[bool] = None,
        final_summary: Optional[str] = None,
    ) -> Optional[Run]:
        run = await self.get_by_id(run_id)
        if not run:
            return None
        run.status = status
        if memory_summary is not None:
            run.memory_summary = memory_summary
        if next_wakeup_at is not None:
            run.next_wakeup_at = next_wakeup_at
        if paused is not None:
            run.paused = paused
        if final_summary is not None:
            run.final_summary = final_summary
        if status in ("COMPLETED", "TERMINATED", "FAILED"):
            run.completed_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(run)
        return run

    async def add_instruction(self, run_id: str, instruction: str) -> Optional[Run]:
        run = await self.get_by_id(run_id)
        if not run:
            return None
        instructions = list(run.extra_instructions or [])
        instructions.append(instruction)
        run.extra_instructions = instructions
        await self.db.commit()
        await self.db.refresh(run)
        return run

    async def update_temporal_id(self, run_id: str, workflow_id: str) -> None:
        run = await self.get_by_id(run_id)
        if run:
            run.temporal_workflow_id = workflow_id
            await self.db.commit()
