"""
Temporal client factory — cached singleton.
"""
from functools import lru_cache
from temporalio.client import Client
from app.core.config import get_settings

_client: Client | None = None


async def get_temporal_client() -> Client:
    """Return a cached Temporal client."""
    global _client
    if _client is None:
        settings = get_settings()
        _client = await Client.connect(settings.temporal_host)
    return _client


async def reset_temporal_client() -> None:
    """Reset client (for testing)."""
    global _client
    _client = None
