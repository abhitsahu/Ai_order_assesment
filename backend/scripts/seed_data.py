"""
Seed default supervisor templates into the database.
Run: python scripts/seed_data.py
"""
import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import AsyncSessionLocal, init_db
from app.db.repositories.supervisor_repository import SupervisorRepository
from app.core.constants import ALL_ACTIONS

TEMPLATES = [
    {
        "name": "Standard Order Ops",
        "base_instruction": (
            "You are a standard order operations supervisor. "
            "Monitor order lifecycle events and take appropriate action to ensure smooth delivery. "
            "Notify relevant teams when issues arise. "
            "Keep the customer informed of significant delays. "
            "Escalate payment issues immediately to the payments team."
        ),
        "available_actions": ALL_ACTIONS,
        "wake_aggressiveness": "moderate",
        "default_wakeup_seconds": 30,
        "model_name": "gemini-3.5-flash",
    },
    {
        "name": "High-Value Order Ops",
        "base_instruction": (
            "You are a high-value order specialist supervisor. "
            "This order requires premium attention. React quickly to any issues. "
            "Always notify the customer proactively of any delays or changes. "
            "Escalate shipment delays immediately to logistics. "
            "Create internal notes for every significant event. "
            "Prioritize speed and customer satisfaction over all else."
        ),
        "available_actions": ALL_ACTIONS,
        "wake_aggressiveness": "aggressive",
        "default_wakeup_seconds": 15,
        "model_name": "gemini-3.5-flash",
    },
    {
        "name": "Conservative Ops",
        "base_instruction": (
            "You are a conservative order supervisor for standard fulfillment orders. "
            "Only intervene when there is a clear problem: payment failure, refund request, or significant delay. "
            "Do not contact the customer unless absolutely necessary. "
            "Log all decisions as internal notes. "
            "Trust the fulfillment process unless something breaks."
        ),
        "available_actions": ALL_ACTIONS,
        "wake_aggressiveness": "conservative",
        "default_wakeup_seconds": 60,
        "model_name": "gemini-3.5-flash",
    },
]


async def seed():
    await init_db()

    async with AsyncSessionLocal() as db:
        repo = SupervisorRepository(db)
        existing = await repo.list_all()
        if existing:
            print(f"Database already has {len(existing)} supervisors. Skipping seed.")
            return

        for template in TEMPLATES:
            supervisor = await repo.create(template)
            print(f"Created supervisor: {supervisor.name} (id={supervisor.id})")

    print("Seed complete!")


if __name__ == "__main__":
    asyncio.run(seed())
