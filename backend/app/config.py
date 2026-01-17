"""
Configuration settings for the chair activity detection system.
"""
import os
from typing import Tuple

# Try to import torch for GPU detection
try:
    import torch
    CUDA_AVAILABLE = torch.cuda.is_available()
except ImportError:
    CUDA_AVAILABLE = False

# Model paths and settings
YOLO_MODEL_PATH = os.getenv("YOLO_MODEL_PATH", "yolov8n.pt")  # Will download if not exists
YOLO_CONFIDENCE_THRESHOLD = float(os.getenv("YOLO_CONFIDENCE_THRESHOLD", "0.25"))
YOLO_IOU_THRESHOLD = float(os.getenv("YOLO_IOU_THRESHOLD", "0.45"))

# COCO class IDs (YOLOv8 uses COCO dataset)
CLASS_ID_CHAIR = 56  # COCO class ID for chair
CLASS_ID_PERSON = 0  # COCO class ID for person
CLASS_ID_TABLE = 60  # COCO class ID for dining table

# Chair-Person Association Thresholds
PERSON_CHAIR_OVERLAP_THRESHOLD = float(os.getenv("PERSON_CHAIR_OVERLAP_THRESHOLD", "0.3"))
PERSON_CHAIR_CENTROID_DISTANCE_THRESHOLD = float(os.getenv("PERSON_CHAIR_CENTROID_DISTANCE_THRESHOLD", "100.0"))

# Hand-Table Detection Thresholds
HAND_TABLE_INTERSECTION_THRESHOLD = float(os.getenv("HAND_TABLE_INTERSECTION_THRESHOLD", "0.3"))  # Lowered from 0.5 to 0.3 for better laptop detection
HAND_KEYPOINT_CONFIDENCE_THRESHOLD = float(os.getenv("HAND_KEYPOINT_CONFIDENCE_THRESHOLD", "0.5"))
HAND_TABLE_PROXIMITY_THRESHOLD = float(os.getenv("HAND_TABLE_PROXIMITY_THRESHOLD", "50.0"))  # Pixels - hands near table also count

# MediaPipe Settings
MEDIAPIPE_HANDS_MODEL_COMPLEXITY = int(os.getenv("MEDIAPIPE_HANDS_MODEL_COMPLEXITY", "1"))  # 0, 1, or 2
MEDIAPIPE_MAX_NUM_HANDS = int(os.getenv("MEDIAPIPE_MAX_NUM_HANDS", "2"))
# Lowered detection confidence for better laptop/desk work detection
MEDIAPIPE_MIN_DETECTION_CONFIDENCE = float(os.getenv("MEDIAPIPE_MIN_DETECTION_CONFIDENCE", "0.4"))  # Lowered from 0.5
MEDIAPIPE_MIN_TRACKING_CONFIDENCE = float(os.getenv("MEDIAPIPE_MIN_TRACKING_CONFIDENCE", "0.4"))  # Lowered from 0.5

# Performance Settings
MAX_FPS = int(os.getenv("MAX_FPS", "10"))
FRAME_SKIP_THRESHOLD = float(os.getenv("FRAME_SKIP_THRESHOLD", "0.1"))  # Skip if processing > 100ms

# Status Colors (BGR format for OpenCV)
STATUS_COLORS = {
    "RED": (0, 0, 255),      # BGR: Red
    "ORANGE": (0, 165, 255),  # BGR: Orange
    "GREEN": (0, 255, 0),     # BGR: Green
}

# API Settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_TITLE = "Chair Activity Detection API"
API_VERSION = "1.0.0"

# Image Processing
MAX_IMAGE_SIZE = (1920, 1080)  # Max width, height
JPEG_QUALITY = int(os.getenv("JPEG_QUALITY", "85"))

# GPU Settings
USE_GPU_ENV = os.getenv("USE_GPU", "auto").lower()
if USE_GPU_ENV == "true":
    USE_GPU = True
elif USE_GPU_ENV == "false":
    USE_GPU = False
else:  # "auto"
    USE_GPU = CUDA_AVAILABLE

DEVICE = "cuda" if USE_GPU and CUDA_AVAILABLE else "cpu"
