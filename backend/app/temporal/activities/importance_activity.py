"""
Importance classifier activity.
Rule-based: determines if an event should immediately wake the agent.
"""
from temporalio import activity
from app.core.constants import (
    IMPORTANT_EVENT_TYPES,
    CONSERVATIVE_EVENTS,
    WakeAggressiveness,
)


@activity.defn(name="classify_importance")
async def classify_importance(event_type: str, wake_aggressiveness: str) -> bool:
    """
    Returns True if this event should immediately wake the main agent.

    Aggressiveness:
    - aggressive: all events wake the agent
    - moderate: important events only (default)
    - conservative: only critical events (payment_failed, refund_requested)
    """
    try:
        if wake_aggressiveness == WakeAggressiveness.AGGRESSIVE:
            return True
        elif wake_aggressiveness == WakeAggressiveness.CONSERVATIVE:
            return event_type in CONSERVATIVE_EVENTS
        else:  # moderate (default)
            return event_type in IMPORTANT_EVENT_TYPES
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(
            f"classify_importance failed for event '{event_type}' (aggressiveness={wake_aggressiveness}): {e}"
        )
        # Fail safe: wake the agent so no event is silently dropped
        return True
