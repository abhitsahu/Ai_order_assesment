"""
TemporalService — thin wrapper over the Temporal client for workflow operations.

Key rule: ALL Temporal RPC calls (signal/query/terminate) must handle
`RPCError: workflow not found` gracefully. This happens when:
  - Temporal dev server was restarted (in-memory history is wiped)
  - Workflow already completed/terminated
In those cases we treat the operation as a no-op or mark the run as stale.
"""
import logging
from temporalio.client import Client
from temporalio.exceptions import WorkflowAlreadyStartedError
from temporalio.service import RPCError
from app.temporal.client import get_temporal_client
from app.temporal.workflows.order_supervisor import OrderSupervisorWorkflow
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def _is_not_found(e: Exception) -> bool:
    """True when a Temporal RPC call failed because the workflow doesn't exist or is already completed."""
    err_str = str(e).lower()
    return isinstance(e, RPCError) and (
        "workflow not found" in err_str or "workflow execution already completed" in err_str
    )


class TemporalService:

    async def _client(self) -> Client:
        return await get_temporal_client()

    async def start_workflow(
        self,
        run_id: str,
        order_id: str,
        supervisor_id: str,
        supervisor_name: str,
        base_instruction: str,
        available_actions: list[str],
        wake_aggressiveness: str,
        default_wakeup_seconds: int,
        order_context: dict,
    ) -> str:
        """Start a new OrderSupervisorWorkflow. Returns the workflow ID."""
        client = await self._client()
        workflow_id = f"order-supervisor-{run_id}"

        try:
            await client.start_workflow(
                OrderSupervisorWorkflow.run,
                args=[
                    run_id, order_id, supervisor_id, supervisor_name,
                    base_instruction, available_actions, wake_aggressiveness,
                    default_wakeup_seconds, order_context,
                ],
                id=workflow_id,
                task_queue=settings.temporal_task_queue,
            )
            logger.info(f"Started workflow {workflow_id}")
        except WorkflowAlreadyStartedError:
            logger.warning(f"Workflow {workflow_id} already started")

        return workflow_id

    async def send_event(self, workflow_id: str, event: dict) -> None:
        try:
            client = await self._client()
            handle = client.get_workflow_handle(workflow_id)
            await handle.signal(OrderSupervisorWorkflow.event_received, event)
            logger.info(f"Sent event signal to {workflow_id}: {event.get('type')}")
        except Exception as e:
            if _is_not_found(e):
                logger.warning(f"Workflow {workflow_id} completed or not found — event dropped: {e}")
                raise ValueError("Workflow execution already completed or not found in Temporal")
            else:
                raise

    async def add_instruction(self, workflow_id: str, instruction: str) -> None:
        try:
            client = await self._client()
            handle = client.get_workflow_handle(workflow_id)
            await handle.signal(OrderSupervisorWorkflow.add_instruction, instruction)
        except Exception as e:
            if _is_not_found(e):
                logger.warning(f"Workflow {workflow_id} completed or not found — instruction dropped: {e}")
                raise ValueError("Workflow execution already completed or not found in Temporal")
            else:
                raise

    async def interrupt(self, workflow_id: str) -> None:
        try:
            client = await self._client()
            handle = client.get_workflow_handle(workflow_id)
            await handle.signal(OrderSupervisorWorkflow.interrupt)
        except Exception as e:
            if _is_not_found(e):
                logger.warning(f"Workflow {workflow_id} not found — interrupt ignored")
            else:
                raise

    async def resume(self, workflow_id: str) -> None:
        try:
            client = await self._client()
            handle = client.get_workflow_handle(workflow_id)
            await handle.signal(OrderSupervisorWorkflow.resume)
        except Exception as e:
            if _is_not_found(e):
                logger.warning(f"Workflow {workflow_id} not found — resume ignored")
            else:
                raise

    async def terminate(self, workflow_id: str) -> None:
        """Terminate gracefully via signal; fall back to force-terminate."""
        try:
            client = await self._client()
            handle = client.get_workflow_handle(workflow_id)
            try:
                await handle.signal(OrderSupervisorWorkflow.terminate_signal)
            except Exception as sig_err:
                if _is_not_found(sig_err):
                    logger.warning(f"Workflow {workflow_id} not found — terminate is a no-op")
                    return
                # Signal failed for another reason — try force terminate
                try:
                    await handle.terminate(reason="User requested termination")
                except Exception as e:
                    if _is_not_found(e):
                        logger.warning(f"Workflow {workflow_id} already gone")
                    else:
                        raise
        except Exception as e:
            if _is_not_found(e):
                logger.warning(f"Workflow {workflow_id} not found — terminate is a no-op")
            else:
                raise

    async def get_state(self, workflow_id: str) -> dict | None:
        """Query the workflow for its current state."""
        try:
            client = await self._client()
            handle = client.get_workflow_handle(workflow_id)
            state = await handle.query(OrderSupervisorWorkflow.get_state)
            return state
        except Exception as e:
            if _is_not_found(e):
                return None  # Workflow gone — caller treats as stale
            logger.warning(f"Could not query workflow {workflow_id}: {e}")
            return None
