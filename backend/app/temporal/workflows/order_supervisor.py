"""
OrderSupervisorWorkflow — the heart of the system.

One workflow instance runs per order. It:
- Maintains durable state (timeline, memory, status)
- Receives events via signals
- Sleeps until timer or important signal
- Wakes and calls the AI agent
- Executes actions returned by agent
- Terminates on terminal events or manual termination
"""
import logging
from datetime import timedelta
from typing import Any, Optional

from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ActivityError

with workflow.unsafe.imports_passed_through():
    from app.core.constants import (
        LogType,
        RunStatus,
        TERMINAL_EVENT_TYPES,
        ActionName,
    )
    from app.core.config import get_settings
    from app.schemas.agent import AgentContext
    from app.agent.memory import compact_timeline, summarize_old_entries

logger = logging.getLogger(__name__)


@workflow.defn(name="OrderSupervisorWorkflow")
class OrderSupervisorWorkflow:
    """Long-running order supervision workflow."""

    def __init__(self) -> None:
        # ── Workflow state ───────────────────────────────────────────────────
        self.timeline: list[dict] = []
        self.memory_summary: str = ""
        self.status: str = RunStatus.CREATED
        self.next_wakeup_in_seconds: int = 30

        # Signal queues / flags
        self.pending_events: list[dict] = []       # buffered incoming events
        self.pending_instructions: list[str] = []  # buffered instructions
        self.signal_received: bool = False          # wake flag for important signal
        self.terminate_requested: bool = False
        self.paused: bool = False
        self.extra_instructions: list[str] = []

        # Supervisor config (set on run())
        self.run_id: str = ""
        self.order_id: str = ""
        self.supervisor_name: str = ""
        self.base_instruction: str = ""
        self.available_actions: list[str] = []
        self.wake_aggressiveness: str = "moderate"
        self.order_context: dict = {}

    # ─── Signal Handlers ─────────────────────────────────────────────────────

    @workflow.signal(name="event_received")
    async def event_received(self, event: dict) -> None:
        """Receive an order event (e.g. payment_confirmed, shipment_delayed)."""
        self.pending_events.append(event)
        self.signal_received = True

    @workflow.signal(name="add_instruction")
    async def add_instruction(self, instruction: str) -> None:
        """Add a run-specific instruction mid-workflow."""
        self.pending_instructions.append(instruction)
        self.signal_received = True

    @workflow.signal(name="interrupt")
    async def interrupt(self) -> None:
        """Pause the workflow."""
        self.paused = True
        self.signal_received = True

    @workflow.signal(name="resume")
    async def resume(self) -> None:
        """Resume after a pause."""
        self.paused = False
        self.signal_received = True

    @workflow.signal(name="terminate")
    async def terminate_signal(self) -> None:
        """Manually terminate the workflow."""
        self.terminate_requested = True
        self.signal_received = True

    # ─── Query Handlers ───────────────────────────────────────────────────────

    @workflow.query(name="get_state")
    def get_state(self) -> dict:
        """Return current workflow state for UI polling."""
        return {
            "run_id": self.run_id,
            "order_id": self.order_id,
            "status": self.status,
            "memory_summary": self.memory_summary,
            "next_wakeup_in_seconds": self.next_wakeup_in_seconds,
            "paused": self.paused,
            "extra_instructions": self.extra_instructions,
            "timeline_count": len(self.timeline),
        }

    # ─── Main Run ─────────────────────────────────────────────────────────────

    @workflow.run
    async def run(
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
    ) -> dict:
        settings = get_settings()

        # Store config in instance
        self.run_id = run_id
        self.order_id = order_id
        self.supervisor_name = supervisor_name
        self.base_instruction = base_instruction
        self.available_actions = available_actions
        self.wake_aggressiveness = wake_aggressiveness
        self.next_wakeup_in_seconds = default_wakeup_seconds
        self.order_context = order_context
        self.status = RunStatus.CREATED

        activity_opts = dict(
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(maximum_attempts=3),
        )

        # ── 1. Log order start & update DB status ─────────────────────────────
        self.status = RunStatus.RUNNING
        await workflow.execute_activity(
            "log_activity",
            args=[run_id, LogType.SYSTEM, {"message": f"Workflow started for order {order_id}"}],
            **activity_opts,
        )
        await workflow.execute_activity(
            "persist_state",
            args=[run_id, RunStatus.RUNNING, self.memory_summary, self.next_wakeup_in_seconds],
            **activity_opts,
        )

        # ── 2. Initial agent run ──────────────────────────────────────────────
        await self._run_agent_cycle("initial_start", activity_opts)

        # ── 3. Main loop ──────────────────────────────────────────────────────
        while not self.terminate_requested:
            # Check continue_as_new (memory compaction)
            if len(self.timeline) >= settings.max_timeline_entries:
                await self._handle_continue_as_new(run_id, order_id, supervisor_id,
                    supervisor_name, base_instruction, available_actions,
                    wake_aggressiveness, default_wakeup_seconds, order_context)
                return {"status": "continued_as_new"}

            # Sleep until: signal arrives OR timer expires
            self.signal_received = False
            self.status = RunStatus.SLEEPING

            await workflow.execute_activity(
                "persist_state",
                args=[run_id, RunStatus.SLEEPING, self.memory_summary, self.next_wakeup_in_seconds],
                **activity_opts,
            )

            await workflow.wait_condition(
                lambda: self.signal_received or self.terminate_requested,
                timeout=timedelta(seconds=self.next_wakeup_in_seconds),
            )

            # ── Handle pause ────────────────────────────────────────────────
            if self.paused:
                self.status = RunStatus.PAUSED
                await workflow.execute_activity(
                    "log_activity",
                    args=[run_id, LogType.INTERRUPT, {"message": "Workflow paused"}],
                    **activity_opts,
                )
                await workflow.execute_activity(
                    "persist_state",
                    args=[run_id, RunStatus.PAUSED, self.memory_summary, None],
                    **activity_opts,
                )
                # Wait for resume or terminate
                await workflow.wait_condition(
                    lambda: not self.paused or self.terminate_requested
                )
                if self.terminate_requested:
                    break
                await workflow.execute_activity(
                    "log_activity",
                    args=[run_id, LogType.RESUME, {"message": "Workflow resumed"}],
                    **activity_opts,
                )

            if self.terminate_requested:
                break

            # ── Drain pending instructions ──────────────────────────────────
            if self.pending_instructions:
                for instr in self.pending_instructions:
                    self.extra_instructions.append(instr)
                    await workflow.execute_activity(
                        "log_activity",
                        args=[run_id, LogType.INSTRUCTION, {"text": instr}],
                        **activity_opts,
                    )
                self.pending_instructions.clear()

            # ── Drain pending events ────────────────────────────────────────
            should_wake_agent = False
            terminal_event_found = False

            while self.pending_events:
                event = self.pending_events.pop(0)
                event_type = event.get("type", "unknown")

                # Log the event
                self._add_to_timeline(LogType.EVENT, {"event_type": event_type, **event.get("payload", {})})
                await workflow.execute_activity(
                    "log_activity",
                    args=[run_id, LogType.EVENT, {"event_type": event_type, **event.get("payload", {})}],
                    **activity_opts,
                )

                # Check terminal
                if event_type in TERMINAL_EVENT_TYPES:
                    terminal_event_found = True
                    self.status = RunStatus.COMPLETED
                    break

                # Classify importance
                is_important = await workflow.execute_activity(
                    "classify_importance",
                    args=[event_type, self.wake_aggressiveness],
                    **activity_opts,
                )
                if is_important:
                    should_wake_agent = True

            # Terminal event → break to final summary
            if terminal_event_found:
                await self._run_final_summary(activity_opts)
                break

            # Determine wake reason
            if should_wake_agent:
                trigger = f"important_signal"
                self.status = RunStatus.RUNNING
                await self._run_agent_cycle(trigger, activity_opts)
            else:
                # Timer-based wake — always run agent
                trigger = "timer"
                self.status = RunStatus.RUNNING
                await self._run_agent_cycle(trigger, activity_opts)

        # ── Termination path ──────────────────────────────────────────────────
        if self.terminate_requested:
            self.status = RunStatus.TERMINATED
            await workflow.execute_activity(
                "log_activity",
                args=[run_id, LogType.TERMINATE, {"message": "Workflow manually terminated"}],
                **activity_opts,
            )
            await workflow.execute_activity(
                "persist_state",
                args=[run_id, RunStatus.TERMINATED, self.memory_summary, None],
                **activity_opts,
            )
            return {"status": RunStatus.TERMINATED, "run_id": run_id}

        return {"status": self.status, "run_id": run_id}

    # ─── Helpers ─────────────────────────────────────────────────────────────

    async def _run_agent_cycle(self, trigger_reason: str, activity_opts: dict) -> None:
        """Run the agent, execute actions, persist state."""
        self.status = RunStatus.RUNNING

        # Log wake
        self._add_to_timeline(LogType.AI_WAKE, {"trigger": trigger_reason})
        await workflow.execute_activity(
            "log_activity",
            args=[self.run_id, LogType.AI_WAKE, {"trigger": trigger_reason, "memory_snapshot": self.memory_summary[:200]}],
            **activity_opts,
        )

        # Build context for agent
        recent = compact_timeline(self.timeline, keep_recent=15)

        context = AgentContext(
            run_id=self.run_id,
            order_id=self.order_id,
            supervisor_name=self.supervisor_name,
            base_instruction=self.base_instruction,
            extra_instructions=self.extra_instructions,
            available_actions=self.available_actions,
            order_context=self.order_context,
            memory_summary=self.memory_summary,
            recent_timeline=recent,
            trigger_reason=trigger_reason,
            wake_aggressiveness=self.wake_aggressiveness,
            default_wakeup_seconds=self.next_wakeup_in_seconds,
        )

        # Call agent
        decision_dict = await workflow.execute_activity(
            "call_agent",
            args=[context.model_dump()],
            start_to_close_timeout=timedelta(minutes=3),
            retry_policy=RetryPolicy(maximum_attempts=2),
        )

        # Update memory
        self.memory_summary = decision_dict.get("memory_summary", self.memory_summary)
        self.next_wakeup_in_seconds = decision_dict.get("next_wakeup_in_seconds", 30)
        actions = decision_dict.get("actions", [])
        action_params = decision_dict.get("action_params", {})

        # Execute actions
        for action_name in actions:
            if action_name not in self.available_actions:
                continue
            message = action_params.get(action_name, f"Action: {action_name}")
            self._add_to_timeline(LogType.ACTION, {"action_name": action_name, "message": message[:200]})
            await workflow.execute_activity(
                "execute_action",
                args=[self.run_id, action_name, message],
                **activity_opts,
            )

        # Log sleep decision
        self._add_to_timeline(
            LogType.SLEEP,
            {
                "next_wakeup_in_seconds": self.next_wakeup_in_seconds,
                "reasoning": decision_dict.get("reasoning", "")[:300],
            },
        )
        await workflow.execute_activity(
            "log_activity",
            args=[
                self.run_id,
                LogType.SLEEP,
                {
                    "next_wakeup_in_seconds": self.next_wakeup_in_seconds,
                    "reasoning": decision_dict.get("reasoning", "")[:300],
                    "actions_taken": actions,
                },
            ],
            **activity_opts,
        )

        # Persist current state
        await workflow.execute_activity(
            "persist_state",
            args=[self.run_id, RunStatus.SLEEPING, self.memory_summary, self.next_wakeup_in_seconds],
            **activity_opts,
        )

    async def _run_final_summary(self, activity_opts: dict) -> None:
        """Run agent one last time to generate final summary."""
        recent = compact_timeline(self.timeline, keep_recent=20)

        context = AgentContext(
            run_id=self.run_id,
            order_id=self.order_id,
            supervisor_name=self.supervisor_name,
            base_instruction=self.base_instruction,
            extra_instructions=self.extra_instructions,
            available_actions=self.available_actions,
            order_context=self.order_context,
            memory_summary=self.memory_summary,
            recent_timeline=recent,
            trigger_reason="workflow_completion",
            wake_aggressiveness=self.wake_aggressiveness,
            default_wakeup_seconds=self.next_wakeup_in_seconds,
        )

        decision_dict = await workflow.execute_activity(
            "call_agent",
            args=[context.model_dump()],
            start_to_close_timeout=timedelta(minutes=3),
            retry_policy=RetryPolicy(maximum_attempts=2),
        )

        final_summary = (
            f"## Final Summary\n\n"
            f"**Order:** {self.order_id}\n\n"
            f"**Reasoning:** {decision_dict.get('reasoning', 'N/A')}\n\n"
            f"**Memory:** {decision_dict.get('memory_summary', self.memory_summary)}\n\n"
            f"**Key Learnings:** Order lifecycle completed. "
            f"Total timeline entries: {len(self.timeline)}."
        )

        await workflow.execute_activity(
            "log_activity",
            args=[self.run_id, LogType.FINAL_SUMMARY, {"summary": final_summary}],
            **activity_opts,
        )

        await workflow.execute_activity(
            "persist_state",
            args=[self.run_id, RunStatus.COMPLETED, decision_dict.get("memory_summary", self.memory_summary), None, final_summary],
            **activity_opts,
        )

    def _add_to_timeline(self, log_type: str, payload: dict) -> None:
        """Add entry to in-memory timeline.
        
        Must use workflow.now() — datetime.now() is banned in the Temporal sandbox.
        """
        self.timeline.append({
            "type": log_type,
            "payload": payload,
            "created_at": workflow.now().isoformat(),
        })

    async def _handle_continue_as_new(
        self,
        run_id: str, order_id: str, supervisor_id: str,
        supervisor_name: str, base_instruction: str,
        available_actions: list[str], wake_aggressiveness: str,
        default_wakeup_seconds: int, order_context: dict,
    ) -> None:
        """Compact history and continue as new to avoid large workflow histories."""
        old_count = len(self.timeline)
        summary_of_old = summarize_old_entries(self.timeline[:-10])

        if summary_of_old:
            if self.memory_summary:
                self.memory_summary = f"{self.memory_summary} | Historical: {summary_of_old}"
            else:
                self.memory_summary = f"Historical: {summary_of_old}"

        self.timeline = compact_timeline(self.timeline, keep_recent=10)

        workflow.logger.info(
            f"continue_as_new triggered: compacted {old_count} → {len(self.timeline)} entries"
        )

        workflow.continue_as_new(
            args=[
                run_id, order_id, supervisor_id, supervisor_name,
                base_instruction, available_actions, wake_aggressiveness,
                default_wakeup_seconds, order_context,
            ]
        )
