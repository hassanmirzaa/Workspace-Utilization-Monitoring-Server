"""
Health check endpoint.
"""
from fastapi import APIRouter
from app.schemas import HealthResponse
from app.config import API_VERSION

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check if the API server is running and healthy.",
    tags=["Health"]
)
async def health_check():
    """
    Health check endpoint.
    
    Returns the current status and version of the API.
    Use this to verify the server is running before making inference requests.
    """
    return HealthResponse(
        status="healthy",
        version=API_VERSION
    )
