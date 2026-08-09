"""
SupervisorService — business logic for supervisor CRUD.
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repositories.supervisor_repository import SupervisorRepository
from app.db.models.supervisor import Supervisor
from app.schemas.supervisor import SupervisorCreate

logger = logging.getLogger(__name__)


class SupervisorService:

    async def create(self, db: AsyncSession, data: SupervisorCreate) -> Supervisor:
        try:
            repo = SupervisorRepository(db)
            return await repo.create(data.model_dump())
        except Exception as e:
            logger.error(f"Failed to create supervisor '{data.name}': {e}", exc_info=True)
            raise

    async def get(self, db: AsyncSession, supervisor_id: str) -> Supervisor | None:
        try:
            repo = SupervisorRepository(db)
            return await repo.get_by_id(supervisor_id)
        except Exception as e:
            logger.error(f"Failed to get supervisor {supervisor_id}: {e}", exc_info=True)
            raise

    async def list_all(self, db: AsyncSession) -> list[Supervisor]:
        try:
            repo = SupervisorRepository(db)
            return await repo.list_all()
        except Exception as e:
            logger.error(f"Failed to list supervisors: {e}", exc_info=True)
            raise

    async def delete(self, db: AsyncSession, supervisor_id: str) -> bool:
        try:
            repo = SupervisorRepository(db)
            return await repo.delete(supervisor_id)
        except Exception as e:
            logger.error(f"Failed to delete supervisor {supervisor_id}: {e}", exc_info=True)
            raise
