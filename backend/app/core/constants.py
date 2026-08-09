"""
Application-wide constants and enumerations.
"""

# ─── Event Types ─────────────────────────────────────────────────────────────

class EventType:
    ORDER_CREATED = "order_created"
    PAYMENT_CONFIRMED = "payment_confirmed"
    PAYMENT_FAILED = "payment_failed"
    SHIPMENT_CREATED = "shipment_created"
    SHIPMENT_DELAYED = "shipment_delayed"
    DELIVERED = "delivered"
    REFUND_REQUESTED = "refund_requested"
    CUSTOMER_MESSAGE_RECEIVED = "customer_message_received"
    NO_UPDATE_FOR_N_HOURS = "no_update_for_n_hours"

ALL_EVENT_TYPES = [
    EventType.ORDER_CREATED,
    EventType.PAYMENT_CONFIRMED,
    EventType.PAYMENT_FAILED,
    EventType.SHIPMENT_CREATED,
    EventType.SHIPMENT_DELAYED,
    EventType.DELIVERED,
    EventType.REFUND_REQUESTED,
    EventType.CUSTOMER_MESSAGE_RECEIVED,
    EventType.NO_UPDATE_FOR_N_HOURS,
]

# Events that immediately wake the agent
IMPORTANT_EVENT_TYPES = {
    EventType.PAYMENT_FAILED,
    EventType.SHIPMENT_DELAYED,
    EventType.REFUND_REQUESTED,
    EventType.CUSTOMER_MESSAGE_RECEIVED,
    EventType.NO_UPDATE_FOR_N_HOURS,
}

# Events that terminate the workflow (when order is "done")
TERMINAL_EVENT_TYPES = {
    EventType.DELIVERED,
    EventType.REFUND_REQUESTED,
}


# ─── Action Names ─────────────────────────────────────────────────────────────

class ActionName:
    MESSAGE_FULFILLMENT_TEAM = "message_fulfillment_team"
    MESSAGE_PAYMENTS_TEAM = "message_payments_team"
    MESSAGE_LOGISTICS_TEAM = "message_logistics_team"
    MESSAGE_CUSTOMER = "message_customer"
    CREATE_INTERNAL_NOTE = "create_internal_note"

ALL_ACTIONS = [
    ActionName.MESSAGE_FULFILLMENT_TEAM,
    ActionName.MESSAGE_PAYMENTS_TEAM,
    ActionName.MESSAGE_LOGISTICS_TEAM,
    ActionName.MESSAGE_CUSTOMER,
    ActionName.CREATE_INTERNAL_NOTE,
]


# ─── Activity Log Types ───────────────────────────────────────────────────────

class LogType:
    EVENT = "EVENT"
    AI_WAKE = "AI_WAKE"
    ACTION = "ACTION"
    SLEEP = "SLEEP"
    INSTRUCTION = "INSTRUCTION"
    FINAL_SUMMARY = "FINAL_SUMMARY"
    INTERRUPT = "INTERRUPT"
    RESUME = "RESUME"
    TERMINATE = "TERMINATE"
    SYSTEM = "SYSTEM"


# ─── Run Status ───────────────────────────────────────────────────────────────

class RunStatus:
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    SLEEPING = "SLEEPING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    TERMINATED = "TERMINATED"
    FAILED = "FAILED"


# ─── Wake Aggressiveness ──────────────────────────────────────────────────────

class WakeAggressiveness:
    AGGRESSIVE = "aggressive"    # wake on every event
    MODERATE = "moderate"        # wake on important events only (default)
    CONSERVATIVE = "conservative"  # wake only on critical events (payment_failed, refund)

CONSERVATIVE_EVENTS = {
    EventType.PAYMENT_FAILED,
    EventType.REFUND_REQUESTED,
}
