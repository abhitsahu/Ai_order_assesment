from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.supervisor import Supervisor


class SupervisorRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> Supervisor:
        supervisor = Supervisor(**data)
        self.db.add(supervisor)
        await self.db.commit()
        await self.db.refresh(supervisor)
        return supervisor

    async def get_by_id(self, supervisor_id: str) -> Optional[Supervisor]:
        result = await self.db.execute(
            select(Supervisor).where(Supervisor.id == supervisor_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Supervisor]:
        result = await self.db.execute(
            select(Supervisor).order_by(Supervisor.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, supervisor_id: str, data: dict) -> Optional[Supervisor]:
        supervisor = await self.get_by_id(supervisor_id)
        if not supervisor:
            return None
        for key, value in data.items():
            setattr(supervisor, key, value)
        await self.db.commit()
        await self.db.refresh(supervisor)
        return supervisor

    async def delete(self, supervisor_id: str) -> bool:
        supervisor = await self.get_by_id(supervisor_id)
        if not supervisor:
            return False
        await self.db.delete(supervisor)
        await self.db.commit()
        return True
