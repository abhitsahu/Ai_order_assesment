from fastapi import APIRouter
from app.api.routes import supervisors, runs, events, instructions, controls

api_router = APIRouter(prefix="/api")

api_router.include_router(supervisors.router)
api_router.include_router(runs.router)
api_router.include_router(events.router)
api_router.include_router(instructions.router)
api_router.include_router(controls.router)
