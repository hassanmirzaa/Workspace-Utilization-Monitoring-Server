"""
Pydantic schemas for request/response models.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    """Bounding box coordinates [x1, y1, x2, y2]."""
    x1: float = Field(..., description="Top-left x coordinate")
    y1: float = Field(..., description="Top-left y coordinate")
    x2: float = Field(..., description="Bottom-right x coordinate")
    y2: float = Field(..., description="Bottom-right y coordinate")


class ChairStatus(BaseModel):
    """Status information for a single chair."""
    chair_id: str = Field(..., description="Unique identifier for the chair")
    status: str = Field(..., description="Status: RED, ORANGE, or GREEN", pattern="^(RED|ORANGE|GREEN)$")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for the status")
    bbox: List[float] = Field(..., min_items=4, max_items=4, description="Bounding box [x1, y1, x2, y2]")


class FrameInferenceResponse(BaseModel):
    """Response model for frame inference endpoint."""
    chairs: List[ChairStatus] = Field(..., description="List of detected chairs with their statuses")
    processing_time_ms: Optional[float] = Field(None, description="Processing time in milliseconds")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")


class VideoFrameResult(BaseModel):
    """Result for a single video frame."""
    timestamp: float = Field(..., description="Timestamp in seconds")
    chairs: List[ChairStatus] = Field(..., description="List of detected chairs with their statuses")


class VideoInferenceResponse(BaseModel):
    """Response model for video inference endpoint."""
    total_frames: int = Field(..., description="Total number of frames processed")
    fps: float = Field(..., description="Frames per second of the video")
    results: List[VideoFrameResult] = Field(..., description="Results for each frame")
    total_processing_time_ms: float = Field(..., description="Total processing time in milliseconds")
