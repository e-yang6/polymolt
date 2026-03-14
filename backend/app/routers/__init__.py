"""API routers — pipeline (AI) and database (placeholder for later)."""

from app.routers.ai_router import router as ai_router
from app.routers.db_router import router as db_router

__all__ = ["ai_router", "db_router"]
