"""
RunService — orchestrates creating runs, starting Temporal workflows, querying state.
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repositories.run_repository import RunRepository
from app.db.repositories.supervisor_repository import SupervisorRepository
from app.db.repositories.activity_repository import ActivityRepository
from app.db.models.run import Run
from app.schemas.run import RunCreate, RunDetail, ActivityLogRead
from app.services.temporal_service import TemporalService
from app.core.constants import RunStatus

logger = logging.getLogger(__name__)


class RunService:

    def __init__(self):
        self.temporal = TemporalService()

    async def create_run(self, db: AsyncSession, data: RunCreate) -> Run:
        supervisor_repo = SupervisorRepository(db)
        supervisor = await supervisor_repo.get_by_id(data.supervisor_id)
        if not supervisor:
            raise ValueError(f"Supervisor {data.supervisor_id} not found")

        run_repo = RunRepository(db)
        run = await run_repo.create({
            "order_id": data.order_id,
            "supervisor_id": data.supervisor_id,
            "status": RunStatus.CREATED,
            "order_context": data.order_context,
            "extra_instructions": [],
        })

        # Start Temporal workflow
        try:
            workflow_id = await self.temporal.start_workflow(
                run_id=run.id,
                order_id=data.order_id,
                supervisor_id=data.supervisor_id,
                supervisor_name=supervisor.name,
                base_instruction=supervisor.base_instruction,
                available_actions=supervisor.available_actions,
                wake_aggressiveness=supervisor.wake_aggressiveness,
                default_wakeup_seconds=supervisor.default_wakeup_seconds,
                order_context=data.order_context,
            )
            await run_repo.update_temporal_id(run.id, workflow_id)
            run.temporal_workflow_id = workflow_id
        except Exception as e:
            logger.error(f"Failed to start workflow: {e}", exc_info=True)
            await run_repo.update_status(run.id, RunStatus.FAILED)
            raise

        return run

    async def get_run(self, db: AsyncSession, run_id: str) -> Run | None:
        run_repo = RunRepository(db)
        return await run_repo.get_by_id(run_id)

    async def get_run_detail(self, db: AsyncSession, run_id: str) -> RunDetail | None:
        run_repo = RunRepository(db)
        run = await run_repo.get_by_id(run_id)
        if not run:
            return None

        activity_repo = ActivityRepository(db)
        logs = await activity_repo.list_for_run(run_id)

        log_reads = [ActivityLogRead.model_validate(l) for l in logs]
        detail = RunDetail.model_validate(run)
        detail.timeline = log_reads
        return detail

    async def list_runs(self, db: AsyncSession) -> list[Run]:
        try:
            run_repo = RunRepository(db)
            return await run_repo.list_all()
        except Exception as e:
            logger.error(f"Failed to list runs: {e}", exc_info=True)
            raise

    async def send_event(self, db: AsyncSession, run_id: str, event: dict) -> None:
        try:
            run_repo = RunRepository(db)
            run = await run_repo.get_by_id(run_id)
            if not run or not run.temporal_workflow_id:
                raise ValueError(f"Run {run_id} not found or has no associated workflow")
            await self.temporal.send_event(run.temporal_workflow_id, event)
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to send event to run {run_id}: {e}", exc_info=True)
            raise

    async def add_instruction(self, db: AsyncSession, run_id: str, instruction: str) -> None:
        try:
            run_repo = RunRepository(db)
            run = await run_repo.get_by_id(run_id)
            if not run or not run.temporal_workflow_id:
                raise ValueError(f"Run {run_id} not found or has no associated workflow")
            await self.temporal.add_instruction(run.temporal_workflow_id, instruction)
            await run_repo.add_instruction(run_id, instruction)
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to add instruction to run {run_id}: {e}", exc_info=True)
            raise

    async def interrupt(self, db: AsyncSession, run_id: str) -> None:
        try:
            run_repo = RunRepository(db)
            run = await run_repo.get_by_id(run_id)
            if not run:
                raise ValueError(f"Run {run_id} not found")
            if run.temporal_workflow_id:
                await self.temporal.interrupt(run.temporal_workflow_id)
            await run_repo.update_status(run_id, RunStatus.PAUSED, paused=True)
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to interrupt run {run_id}: {e}", exc_info=True)
            raise

    async def resume(self, db: AsyncSession, run_id: str) -> None:
        try:
            run_repo = RunRepository(db)
            run = await run_repo.get_by_id(run_id)
            if not run:
                raise ValueError(f"Run {run_id} not found")
            if run.temporal_workflow_id:
                await self.temporal.resume(run.temporal_workflow_id)
            await run_repo.update_status(run_id, RunStatus.RUNNING, paused=False)
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to resume run {run_id}: {e}", exc_info=True)
            raise

    async def terminate(self, db: AsyncSession, run_id: str) -> None:
        try:
            run_repo = RunRepository(db)
            run = await run_repo.get_by_id(run_id)
            if not run:
                raise ValueError(f"Run {run_id} not found")
            if run.temporal_workflow_id:
                await self.temporal.terminate(run.temporal_workflow_id)
            await run_repo.update_status(run_id, RunStatus.TERMINATED)
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to terminate run {run_id}: {e}", exc_info=True)
            raise
