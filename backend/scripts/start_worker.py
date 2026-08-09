"""
Standalone script to run the Temporal worker.
Run this in a separate terminal: python scripts/start_worker.py
"""
import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.logging import setup_logging
from app.temporal.worker import run_worker

if __name__ == "__main__":
    setup_logging()
    print("Starting Temporal worker... (Ctrl+C to stop)")
    asyncio.run(run_worker())
