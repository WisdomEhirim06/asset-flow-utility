"""Health-check endpoint."""

from fastapi import APIRouter

from app.config import settings
from app.schemas import HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns the current health status and version of the API.",
)
async def health_check() -> HealthResponse:
    return HealthResponse(status="healthy", version=settings.app_version)
