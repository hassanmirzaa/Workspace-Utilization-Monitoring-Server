"""
Frame inference endpoints.
"""
import time
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
from typing import Optional
import numpy as np

from app.schemas import FrameInferenceResponse, ChairStatus, VideoInferenceResponse, VideoFrameResult
from app.utils.image import decode_image, encode_image
from app.utils.draw import draw_all_chairs
from app.utils.video import extract_frames_from_video, create_video_from_frames
import tempfile
import os
from app.services.detector import YOLODetector
from app.services.pose import HandDetector
from app.services.chair_mapper import ChairMapper
from app.services.status_engine import StatusEngine

router = APIRouter()

# Initialize services (singleton pattern)
_detector: Optional[YOLODetector] = None
_hand_detector: Optional[HandDetector] = None
_chair_mapper: Optional[ChairMapper] = None
_status_engine: Optional[StatusEngine] = None


def get_services():
    """Get or initialize service instances."""
    global _detector, _hand_detector, _chair_mapper, _status_engine
    
    if _detector is None:
        _detector = YOLODetector()
        _hand_detector = HandDetector()
        _chair_mapper = ChairMapper(_detector)
        _status_engine = StatusEngine(_chair_mapper, _hand_detector)
    
    return _detector, _hand_detector, _chair_mapper, _status_engine


@router.post(
    "/frame",
    response_model=FrameInferenceResponse,
    summary="Process Image Frame",
    description="""
    Process a single image frame and return chair statuses in JSON format.
    
    **Color Logic:**
    - 🔴 **RED**: Chair detected, no person sitting
    - 🟠 **ORANGE**: Person sitting, hands NOT on table
    - 🟢 **GREEN**: Person sitting, hands ON table
    
    **Supported Formats:** JPEG, PNG
    
    **Response includes:**
    - Chair IDs
    - Status (RED/ORANGE/GREEN)
    - Confidence scores
    - Bounding box coordinates [x1, y1, x2, y2]
    - Processing time
    """,
    response_description="JSON response with detected chairs and their statuses",
    tags=["Image Processing"]
)
async def infer_frame(
    file: UploadFile = File(..., description="Image file (JPEG or PNG)", example="test_image.jpg"),
    camera_id: Optional[str] = Form(None, description="Optional camera identifier for tracking")
):
    """
    Process a camera frame and return chair statuses.
    
    Upload an image to detect chairs and determine their activity status.
    """
    start_time = time.time()
    
    try:
        # Read and decode image
        image_bytes = await file.read()
        image = decode_image(image_bytes)
        
        # Get services
        detector, hand_detector, _, status_engine = get_services()
        
        # Step 1: Detect objects (chairs, persons, tables)
        detections = detector.detect(image)
        chairs = detections.get('chairs', [])
        persons = detections.get('persons', [])
        tables = detections.get('tables', [])
        
        # Step 2: Detect hands
        hands = hand_detector.detect_hands(image)
        
        # Step 3: Determine statuses
        results = status_engine.process_frame(chairs, persons, tables, hands)
        
        # Convert to response format
        chair_statuses = [
            ChairStatus(
                chair_id=result['chair_id'],
                status=result['status'],
                confidence=result['confidence'],
                bbox=result['bbox']
            )
            for result in results
        ]
        
        processing_time = (time.time() - start_time) * 1000  # Convert to ms
        
        return FrameInferenceResponse(
            chairs=chair_statuses,
            processing_time_ms=processing_time
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/frame/annotated",
    summary="Process Image Frame (Annotated)",
    description="""
    Process a single image frame and return annotated image with colored bounding boxes.
    
    **Color Coding:**
    - 🔴 **RED boxes**: Empty chair (no person sitting)
    - 🟠 **ORANGE boxes**: Person sitting, hands NOT on table
    - 🟢 **GREEN boxes**: Person sitting, hands ON table
    
    **Supported Formats:** JPEG, PNG (input) → JPEG (output)
    
    The returned image will have colored bounding boxes drawn around each detected chair
    with labels showing chair ID, status, and confidence score.
    """,
    response_description="JPEG image with colored bounding boxes and labels",
    tags=["Image Processing"]
)
async def infer_frame_annotated(
    file: UploadFile = File(..., description="Image file (JPEG or PNG)", example="test_image.jpg"),
    camera_id: Optional[str] = Form(None, description="Optional camera identifier")
):
    """
    Process a camera frame and return annotated image with colored boxes.
    
    Returns the same image with colored bounding boxes drawn on detected chairs.
    """
    try:
        # Read and decode image
        image_bytes = await file.read()
        image = decode_image(image_bytes)
        
        # Get services
        detector, hand_detector, _, status_engine = get_services()
        
        # Step 1: Detect objects
        detections = detector.detect(image)
        chairs = detections.get('chairs', [])
        persons = detections.get('persons', [])
        tables = detections.get('tables', [])
        
        # Step 2: Detect hands
        hands = hand_detector.detect_hands(image)
        
        # Step 3: Determine statuses
        results = status_engine.process_frame(chairs, persons, tables, hands)
        
        # Step 4: Draw annotations
        annotated_image = draw_all_chairs(image, results)
        
        # Encode and return
        encoded_image = encode_image(annotated_image, format="JPEG")
        
        return Response(
            content=encoded_image,
            media_type="image/jpeg"
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/video",
    response_model=VideoInferenceResponse,
    summary="Process Video (JSON)",
    description="""
    Process a video file and return chair statuses for each frame in JSON format.
    
    **Color Logic:**
    - 🔴 **RED**: Chair detected, no person sitting
    - 🟠 **ORANGE**: Person sitting, hands NOT on table
    - 🟢 **GREEN**: Person sitting, hands ON table
    
    **Supported Formats:** MP4, M4V, AVI, MOV, and other OpenCV-supported formats
    
    **Parameters:**
    - `process_fps`: Frames per second to process (default: Auto - 20% of video FPS, min 5, max 30)
      - If None: Automatically uses 20% of video FPS (e.g., 60 FPS video → 12 FPS processing)
      - For 60-90 FPS videos: Recommended 10-20 FPS
      - Lower values = faster processing but less frequent detection
      - Higher values = slower processing but more accurate tracking
    
    **Response includes:**
    - Total frames processed
    - Results for each frame with timestamp
    - Chair statuses per frame
    - Total processing time
    """,
    response_description="JSON response with frame-by-frame chair detection results",
    tags=["Video Processing"]
)
async def infer_video(
    file: UploadFile = File(..., description="Video file (MP4, M4V, AVI, MOV, etc.)", example="test_video.mp4"),
    camera_id: Optional[str] = Form(None, description="Optional camera identifier for tracking"),
    process_fps: Optional[float] = Form(None, description="FPS to process video at. If None, uses 20% of video FPS (min 5, max 30). For 60-90 FPS videos, recommended: 10-20")
):
    """
    Process a video and return chair statuses for each frame.
    
    Upload a video file to get frame-by-frame chair detection results.
    """
    start_time = time.time()
    
    try:
        # Read video bytes
        video_bytes = await file.read()
        
        # Get file extension from filename
        filename = file.filename or "video.mp4"
        file_ext = os.path.splitext(filename)[1] or '.mp4'
        
        # Get services
        detector, hand_detector, _, status_engine = get_services()
        
        # Process frames
        frame_results = []
        total_frames = 0
        video_fps = 30.0  # Default, will be updated from video
        actual_process_fps = None
        
        for frame, timestamp, original_fps in extract_frames_from_video(video_bytes, fps=None, file_extension=file_ext):
            if total_frames == 0:
                video_fps = original_fps
                # Auto-calculate process_fps if not provided
                if process_fps is None:
                    # Use 20% of original FPS, but clamp between 5 and 30 FPS
                    actual_process_fps = max(5.0, min(30.0, original_fps * 0.2))
                    print(f"Video FPS: {original_fps}, Auto-set process_fps to: {actual_process_fps}")
                else:
                    actual_process_fps = process_fps
                
                # Only process frames at the specified rate
                detect_interval = max(1, int(original_fps / actual_process_fps)) if actual_process_fps < original_fps else 1
            
            total_frames += 1
            
            # Only detect every N frames based on process_fps
            if total_frames % detect_interval != 0:
                # Skip this frame for detection (but we still need to add a result)
                # Reuse last result or empty result
                if frame_results:
                    last_result = frame_results[-1]
                    frame_results.append(
                        VideoFrameResult(
                            timestamp=timestamp,
                            chairs=last_result.chairs  # Reuse last detection
                        )
                    )
                else:
                    frame_results.append(
                        VideoFrameResult(
                            timestamp=timestamp,
                            chairs=[]
                        )
                    )
                continue
            
            # Detect objects (only on frames we're processing)
            detections = detector.detect(frame)
            chairs = detections.get('chairs', [])
            persons = detections.get('persons', [])
            tables = detections.get('tables', [])
            
            # Detect hands
            hands = hand_detector.detect_hands(frame)
            
            # Determine statuses
            results = status_engine.process_frame(chairs, persons, tables, hands)
            
            # Convert to response format
            chair_statuses = [
                ChairStatus(
                    chair_id=result['chair_id'],
                    status=result['status'],
                    confidence=result['confidence'],
                    bbox=result['bbox']
                )
                for result in results
            ]
            
            frame_results.append(
                VideoFrameResult(
                    timestamp=timestamp,
                    chairs=chair_statuses
                )
            )
        
        total_processing_time = (time.time() - start_time) * 1000
        
        return VideoInferenceResponse(
            total_frames=total_frames,
            fps=video_fps,
            results=frame_results,
            total_processing_time_ms=total_processing_time
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/video/annotated",
    summary="Process Video (Annotated)",
    description="""
    Process a video file and return annotated video with colored bounding boxes on chairs.
    
    **Color Coding:**
    - 🔴 **RED boxes**: Empty chair (no person sitting)
    - 🟠 **ORANGE boxes**: Person sitting, hands NOT on table
    - 🟢 **GREEN boxes**: Person sitting, hands ON table
    
    **Supported Formats:** MP4, AVI, MOV (input) → MP4 (output)
    
    **Parameters:**
    - `process_fps`: Frames per second to process (default: Auto - 20% of video FPS, min 5, max 30)
      - If None: Automatically uses 20% of video FPS (e.g., 60 FPS video → 12 FPS processing)
      - For 60-90 FPS videos: Recommended 10-20 FPS
      - Lower values = faster processing but less frequent detection
      - Higher values = slower processing but more accurate tracking
    
    The returned video will have colored bounding boxes drawn around each detected chair
    in every frame, with labels showing chair ID, status, and confidence score.
    
    **Note:** Processing time depends on video length and process_fps setting.
    """,
    response_description="MP4 video file with colored bounding boxes and labels on each frame",
    tags=["Video Processing"]
)
async def infer_video_annotated(
    file: UploadFile = File(..., description="Video file (MP4, M4V, AVI, MOV, etc.)", example="test_video.mp4"),
    camera_id: Optional[str] = Form(None, description="Optional camera identifier"),
    process_fps: Optional[float] = Form(None, description="FPS to process video at. If None, uses 20% of video FPS (min 5, max 30). For 60-90 FPS videos, recommended: 10-20")
):
    """
    Process a video and return annotated video with colored boxes on chairs.
    
    Upload a video file to get an annotated version with colored bounding boxes.
    """
    try:
        # Read video bytes
        video_bytes = await file.read()
        
        # Get file extension from filename
        filename = file.filename or "video.mp4"
        file_ext = os.path.splitext(filename)[1] or '.mp4'
        
        # Get services
        detector, hand_detector, _, status_engine = get_services()
        
        # Process frames and collect annotated frames
        annotated_frames = []
        video_fps = 30.0
        frame_width = None
        frame_height = None
        last_results = []  # Store last detection results for frames we skip
        frame_index = 0
        actual_process_fps = None  # Will be set after we know video FPS
        
        detect_interval = 1  # Will be calculated after we know video FPS
        
        for frame, timestamp, original_fps in extract_frames_from_video(video_bytes, fps=None, file_extension=file_ext):
            if frame_width is None:
                frame_height, frame_width = frame.shape[:2]
                video_fps = original_fps
                
                # Auto-calculate process_fps if not provided
                if process_fps is None:
                    # Use 20% of original FPS, but clamp between 5 and 30 FPS
                    actual_process_fps = max(5.0, min(30.0, original_fps * 0.2))
                    print(f"Video FPS: {original_fps}, Auto-set process_fps to: {actual_process_fps}")
                else:
                    actual_process_fps = process_fps
                
                # Calculate how often to run detection
                if actual_process_fps and actual_process_fps < original_fps:
                    detect_interval = max(1, int(original_fps / actual_process_fps))
                else:
                    detect_interval = 1  # Detect every frame if process_fps >= original_fps
            
            # Only run detection every N frames (based on process_fps)
            # But include ALL frames in output video
            should_detect = (frame_index == 0) or (frame_index % detect_interval == 0)
            
            if should_detect:
                # Detect objects
                detections = detector.detect(frame)
                chairs = detections.get('chairs', [])
                persons = detections.get('persons', [])
                tables = detections.get('tables', [])
                
                # Detect hands
                hands = hand_detector.detect_hands(frame)
                
                # Determine statuses
                results = status_engine.process_frame(chairs, persons, tables, hands)
                last_results = results
            else:
                # Reuse last detection results for intermediate frames
                results = last_results
            
            # Draw annotations on every frame
            annotated_frame = draw_all_chairs(frame.copy(), results)
            annotated_frames.append(annotated_frame)
            frame_index += 1
        
        # Create output video
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
            output_path = tmp_file.name
        
        try:
            create_video_from_frames(
                annotated_frames,
                output_path,
                fps=video_fps,  # Use original video FPS, not process_fps
                width=frame_width,
                height=frame_height
            )
            
            # Read and return video
            with open(output_path, 'rb') as f:
                video_data = f.read()
            
            return Response(
                content=video_data,
                media_type="video/mp4",
                headers={
                    "Content-Disposition": "attachment; filename=annotated_video.mp4"
                }
            )
        
        finally:
            # Clean up temp file
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
