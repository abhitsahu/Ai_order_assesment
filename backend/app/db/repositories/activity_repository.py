from datetime import datetime
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.activity_log import ActivityLog


class ActivityRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def append(self, run_id: str, log_type: str, payload: dict) -> ActivityLog:
        entry = ActivityLog(run_id=run_id, type=log_type, payload=payload)
        self.db.add(entry)
        await self.db.commit()
        await self.db.refresh(entry)
        return entry

    async def list_for_run(self, run_id: str) -> list[ActivityLog]:
        result = await self.db.execute(
            select(ActivityLog)
            .where(ActivityLog.run_id == run_id)
            .order_by(ActivityLog.created_at.asc())
        )
        return list(result.scalars().all())

    async def list_for_run_paginated(
        self, run_id: str, limit: int = 200, offset: int = 0
    ) -> list[ActivityLog]:
        result = await self.db.execute(
            select(ActivityLog)
            .where(ActivityLog.run_id == run_id)
            .order_by(ActivityLog.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def count_for_run(self, run_id: str) -> int:
        from sqlalchemy import func
        result = await self.db.execute(
            select(func.count()).where(ActivityLog.run_id == run_id)
        )
        return result.scalar_one()
