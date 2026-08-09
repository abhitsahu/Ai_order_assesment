from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


def _make_async_url(url: str) -> str:
    """
    Convert any postgres:// or postgresql:// URL to the asyncpg driver format.
    Supabase provides: postgresql://user:pass@host:port/db
    SQLAlchemy async needs: postgresql+asyncpg://user:pass@host:port/db
    """
    for prefix in ("postgresql://", "postgres://"):
        if url.startswith(prefix):
            return "postgresql+asyncpg://" + url[len(prefix):]
    return url  # already has driver or is empty


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database — accepts Supabase's postgresql:// or postgresql+asyncpg://
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_supervisor"

    # Temporal
    temporal_host: str = "localhost:7233"
    temporal_namespace: str = "default"
    temporal_task_queue: str = "order-supervisor"

    # Gemini
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash"


    # Agent defaults
    default_wakeup_seconds: int = 30
    max_timeline_entries: int = 100  # trigger continue_as_new above this

    # App
    app_env: str = "development"
    log_level: str = "INFO"
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    @property
    def async_database_url(self) -> str:
        """Always return the asyncpg-compatible URL."""
        return _make_async_url(self.database_url)


@lru_cache
def get_settings() -> Settings:
    return Settings()
