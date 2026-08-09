"""
Temporal worker — registers all workflows and activities.
"""
import asyncio
import logging
from temporalio.worker import Worker
from app.temporal.client import get_temporal_client
from app.core.config import get_settings

# Workflows
from app.temporal.workflows.order_supervisor import OrderSupervisorWorkflow

# Activities
from app.temporal.activities.importance_activity import classify_importance
from app.temporal.activities.agent_activity import call_agent
from app.temporal.activities.action_activity import execute_action
from app.temporal.activities.persistence_activity import persist_state, log_activity

logger = logging.getLogger(__name__)


async def run_worker() -> None:
    settings = get_settings()
    client = await get_temporal_client()

    worker = Worker(
        client,
        task_queue=settings.temporal_task_queue,
        workflows=[OrderSupervisorWorkflow],
        activities=[
            classify_importance,
            call_agent,
            execute_action,
            persist_state,
            log_activity,
        ],
    )

    logger.info(f"Starting Temporal worker on queue: {settings.temporal_task_queue}")
    await worker.run()


if __name__ == "__main__":
    from app.core.logging import setup_logging
    setup_logging()
    asyncio.run(run_worker())
