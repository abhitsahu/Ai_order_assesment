"""
Memory management: context compaction for long-running workflows.
"""


def compact_timeline(timeline: list[dict], keep_recent: int = 10) -> list[dict]:
    """
    Keep the most recent N timeline entries for agent context.
    Older entries are summarized into the memory_summary instead.
    """
    if len(timeline) <= keep_recent:
        return timeline
    return timeline[-keep_recent:]


def should_compact(timeline: list[dict], threshold: int = 20) -> bool:
    """Return True if the timeline is large enough to need compaction."""
    return len(timeline) > threshold


def summarize_old_entries(old_entries: list[dict]) -> str:
    """
    Create a brief text summary of older timeline entries.
    This is appended to memory_summary to avoid losing context.
    """
    if not old_entries:
        return ""

    event_types = {}
    actions_taken = []

    for entry in old_entries:
        t = entry.get("type", "UNKNOWN")
        payload = entry.get("payload", {})

        if t == "EVENT":
            event_name = payload.get("event_type", "unknown_event")
            event_types[event_name] = event_types.get(event_name, 0) + 1
        elif t == "ACTION":
            action = payload.get("action_name", "unknown_action")
            actions_taken.append(action)

    parts = []
    if event_types:
        events_str = ", ".join(f"{k}(x{v})" for k, v in event_types.items())
        parts.append(f"Past events: {events_str}")
    if actions_taken:
        parts.append(f"Past actions: {', '.join(set(actions_taken))}")

    return "; ".join(parts) if parts else "Prior activity recorded."
