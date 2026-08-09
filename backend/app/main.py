"""
FastAPI application entry point.
"""
import asyncio
import logging
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db.database import init_db
from app.api.router import api_router

setup_logging()
logger = logging.getLogger(__name__)
settings = get_settings()


def _start_worker_thread() -> None:
    """Run Temporal worker in a background thread with continuous auto-reconnect."""
    import asyncio
    import time
    from app.temporal.worker import run_worker

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    while True:
        try:
            loop.run_until_complete(run_worker())
            logger.warning("Temporal worker stopped; reconnecting in 5s...")
        except Exception as e:
            logger.warning(f"Temporal worker loop error: {e}. Reconnecting in 5s...")
        time.sleep(5)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AI Order Supervisor API...")

    # Initialize database tables
    await init_db()
    logger.info("Database initialized")

    # Start Temporal worker in background thread
    worker_thread = threading.Thread(
        target=_start_worker_thread, daemon=True, name="temporal-worker"
    )
    worker_thread.start()
    logger.info("Temporal worker started in background thread")

    yield

    logger.info("Shutting down...")


app = FastAPI(
    title="AI Order Supervisor",
    description="Long-running AI supervisor for order lifecycle management",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Catch-all so unhandled errors return JSON with CORS headers (not a bare 500)."""
    from fastapi.responses import JSONResponse
    logger.error(f"Unhandled exception on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
        headers={"Access-Control-Allow-Origin": "*"},
    )

app.include_router(api_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "AI Order Supervisor"}
