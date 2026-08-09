"""
Main entry point — can run API or worker.
Usage:
  uv run uvicorn app.main:app --reload --port 8000   # API + worker thread
  uv run python scripts/start_worker.py               # standalone worker
"""
from app.main import app  # noqa: F401
