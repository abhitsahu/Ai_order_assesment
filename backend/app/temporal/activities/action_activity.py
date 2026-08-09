"""
Action executor activity — dispatches to one of the 5 business actions.
"""
import logging
from temporalio import activity
from app.core.constants import ActionName
from app.db.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

ACTION_REGISTRY = {
    ActionName.MESSAGE_FULFILLMENT_TEAM: "app.actions.fulfillment.message_fulfillment_team",
    ActionName.MESSAGE_PAYMENTS_TEAM: "app.actions.payments.message_payments_team",
    ActionName.MESSAGE_LOGISTICS_TEAM: "app.actions.logistics.message_logistics_team",
    ActionName.MESSAGE_CUSTOMER: "app.actions.customer.message_customer",
    ActionName.CREATE_INTERNAL_NOTE: "app.actions.internal_note.create_internal_note",
}


@activity.defn(name="execute_action")
async def execute_action(run_id: str, action_name: str, message: str) -> dict:
    """
    Execute a named business action by looking it up in the registry.
    Each action writes to the activity_log table.
    """
    activity.heartbeat(f"Executing action: {action_name}")

    module_path = ACTION_REGISTRY.get(action_name)
    if not module_path:
        logger.warning(f"Unknown action: {action_name} for run {run_id}")
        return {"error": f"Unknown action: {action_name}"}

    try:
        # Dynamically import the action function
        parts = module_path.rsplit(".", 1)
        module = __import__(parts[0], fromlist=[parts[1]])
        fn = getattr(module, parts[1])

        async with AsyncSessionLocal() as db:
            result = await fn(run_id=run_id, message=message, db=db)

        logger.info(f"Executed action {action_name} for run {run_id}")
        return result
    except ImportError as e:
        logger.error(f"Failed to import action module '{module_path}' for run {run_id}: {e}")
        return {"error": f"Action module import failed: {str(e)}"}
    except AttributeError as e:
        logger.error(f"Action function not found in module '{module_path}' for run {run_id}: {e}")
        return {"error": f"Action function not found: {str(e)}"}
    except Exception as e:
        logger.error(f"Action '{action_name}' failed for run {run_id}: {e}", exc_info=True)
        # Return an error dict instead of crashing the activity — non-critical actions
        # should not crash the entire workflow
        return {"error": f"Action failed: {str(e)}"}
