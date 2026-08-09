import json
import re
import logging
from typing import Optional
from google import genai
from google.genai import types as genai_types
from app.core.config import get_settings
from app.schemas.agent import AgentDecision, AgentContext
from app.agent.prompts import build_agent_prompt

logger = logging.getLogger(__name__)
settings = get_settings()

# Module-level client — created once
_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


def _extract_json(text: str) -> Optional[dict]:
    """Extract JSON from model response, handling markdown code blocks."""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Strip markdown code fences
    match = re.search(r"```(?:json)?\s*([\s\S]+?)```", text)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Find first { ... } block
    match = re.search(r"\{[\s\S]+\}", text)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    return None


async def run_agent(context: AgentContext) -> AgentDecision:
    """
    Call the Gemini model with the agent context and return a structured decision.
    Falls back to a safe default if the model fails or returns invalid JSON.
    """
    import asyncio
    context_dict = context.model_dump()
    system_prompt, user_message = build_agent_prompt(context_dict)

    try:
        client = _get_client()

        # google-genai's generate_content is synchronous — run in thread pool
        # to avoid blocking the asyncio event loop in Temporal activities.
        def _call():
            return client.models.generate_content(
                model=settings.gemini_model,
                contents=user_message,
                config=genai_types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.3,
                    max_output_tokens=1024,
                ),
            )

        response = await asyncio.to_thread(_call)
        raw_text = response.text
        logger.debug(f"Agent raw response: {raw_text[:500]}")

        parsed = _extract_json(raw_text)
        if not parsed:
            logger.warning(f"Agent returned non-JSON response: {raw_text[:200]}")
            return _fallback_decision(context)

        decision = AgentDecision(**parsed)
        # Clamp wakeup to reasonable bounds
        decision.next_wakeup_in_seconds = max(
            5, min(decision.next_wakeup_in_seconds, 3600)
        )
        return decision

    except Exception as e:
        logger.error(f"Agent call failed: {e}", exc_info=True)
        return _fallback_decision(context)


def _fallback_decision(context: AgentContext) -> AgentDecision:
    """Return a safe no-op decision when the agent fails."""
    return AgentDecision(
        reasoning="Agent call failed; defaulting to no-op sleep.",
        actions=[],
        action_params={},
        memory_summary=context.memory_summary or "Monitoring order. No memory yet.",
        next_wakeup_in_seconds=context.default_wakeup_seconds,
        recommend_close=False,
    )
