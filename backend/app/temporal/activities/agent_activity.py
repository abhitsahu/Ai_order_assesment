"""
Agent activity — calls the Gemini LLM agent.
"""
import logging
from temporalio import activity
from app.schemas.agent import AgentContext, AgentDecision
from app.agent.agent import run_agent

logger = logging.getLogger(__name__)


@activity.defn(name="call_agent")
async def call_agent(context: dict) -> dict:
    """
    Deserialize context, call the Gemini agent, return serialized decision.
    Falls back to a safe no-op if the agent call fails.
    """
    activity.heartbeat("Calling Gemini agent...")

    try:
        ctx = AgentContext(**context)
    except Exception as e:
        logger.error(f"Failed to deserialize AgentContext: {e}", exc_info=True)
        # Return a minimal fallback so the workflow doesn't crash
        return AgentDecision(
            reasoning=f"Context deserialization failed: {e}",
            actions=[],
            action_params={},
            memory_summary=context.get("memory_summary", ""),
            next_wakeup_in_seconds=context.get("default_wakeup_seconds", 30),
            recommend_close=False,
        ).model_dump()

    try:
        decision: AgentDecision = await run_agent(ctx)

        logger.info(
            f"Agent decision for run {ctx.run_id}: "
            f"actions={decision.actions}, "
            f"sleep={decision.next_wakeup_in_seconds}s, "
            f"recommend_close={decision.recommend_close}"
        )
        return decision.model_dump()

    except Exception as e:
        logger.error(
            f"Agent call failed for run {ctx.run_id} "
            f"(trigger={context.get('trigger_reason')}, model={context.get('model_name', 'unknown')}): {e}",
            exc_info=True,
        )
        # Fallback: don't crash the workflow, just sleep and retry next cycle
        return AgentDecision(
            reasoning=f"Agent call failed ({type(e).__name__}): {str(e)[:200]}",
            actions=[],
            action_params={},
            memory_summary=ctx.memory_summary or "Agent unavailable; monitoring continues.",
            next_wakeup_in_seconds=ctx.default_wakeup_seconds,
            recommend_close=False,
        ).model_dump()
