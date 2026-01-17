"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import API_TITLE, API_VERSION, API_HOST, API_PORT
from app.routes import infer, health

# Create FastAPI app with enhanced Swagger documentation
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description="""
    ## Chair Activity Detection API
    
    Production-ready MVP for real-time chair activity detection using YOLOv8 and MediaPipe.
    
    ### Features:
    - **YOLOv8 Object Detection**: Detects chairs, persons, and tables
    - **MediaPipe Hand Detection**: Detects hand keypoints
    - **Three-State Classification**:
      - 🔴 **RED**: Chair detected, no person sitting
      - 🟠 **ORANGE**: Person sitting, hands NOT on table
      - 🟢 **GREEN**: Person sitting, hands ON table
    
    ### Usage:
    1. Upload an image or video file
    2. Get chair statuses with bounding boxes
    3. Optionally get annotated images/videos with colored boxes
    
    All endpoints support both image and video processing.
    """,
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
    openapi_url="/openapi.json"  # OpenAPI schema
)

# Configure CORS for Flutter mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Flutter app's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(infer.router, prefix="/infer", tags=["inference"])
app.include_router(health.router, tags=["health"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Chair Activity Detection API",
        "version": API_VERSION,
        "endpoints": {
            "health": "/health",
            "infer_frame": "/infer/frame",
            "infer_frame_annotated": "/infer/frame/annotated",
            "infer_video": "/infer/video",
            "infer_video_annotated": "/infer/video/annotated"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=False  # Set to True for development
    )
