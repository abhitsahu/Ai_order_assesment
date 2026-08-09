from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
from app.core.config import get_settings

settings = get_settings()

# Supabase requires SSL; asyncpg accepts it via connect_args
_connect_args = {}
if "supabase.co" in settings.database_url or "pooler.supabase" in settings.database_url:
    _connect_args = {"ssl": "require"}

# NullPool is required because Temporal activities run in a separate thread
# with its own event loop. A connection pool would bind connections to one
# event loop and cause "Future attached to a different loop" errors when
# activities use the same engine from a different loop.
# Supabase's session pooler (port 5432) handles external connection pooling.
engine = create_async_engine(
    settings.async_database_url,
    echo=False,
    pool_pre_ping=True,
    poolclass=NullPool,
    connect_args=_connect_args,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    """FastAPI dependency for database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Create all tables. Uses Supabase Postgres via asyncpg."""
    async with engine.begin() as conn:
        from app.db.models import supervisor, run, activity_log  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)
