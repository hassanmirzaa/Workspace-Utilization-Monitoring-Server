"""
Video processing utilities.
"""
import cv2
import numpy as np
from typing import Iterator, Tuple, Optional
import tempfile
import os


def extract_frames_from_video(video_bytes: bytes, fps: Optional[int] = None, file_extension: str = '.mp4') -> Iterator[Tuple[np.ndarray, float, float]]:
    """
    Extract frames from video bytes.
    
    Args:
        video_bytes: Raw video file bytes
        fps: Optional target FPS for processing (None = process all frames)
        file_extension: File extension (e.g., '.mp4', '.m4v', '.avi', '.mov')
        
    Yields:
        Tuple of (frame_image, timestamp_in_seconds, original_fps)
    """
    # Normalize extension
    if not file_extension.startswith('.'):
        file_extension = '.' + file_extension
    
    # Save to temporary file with proper extension
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
        tmp_file.write(video_bytes)
        tmp_path = tmp_file.name
    
    try:
        # Open video
        cap = cv2.VideoCapture(tmp_path)
        
        if not cap.isOpened():
            raise ValueError("Failed to open video file")
        
        original_fps = cap.get(cv2.CAP_PROP_FPS)
        if original_fps <= 0:
            original_fps = 30.0  # Default if FPS not available
        
        frame_count = 0
        current_time = 0.0
        process_every_n = 1
        
        # Calculate how often to process (for detection)
        if fps and fps < original_fps:
            process_every_n = max(1, int(original_fps / fps))
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Yield all frames, but mark which ones to process
            should_process = (frame_count % process_every_n == 0)
            
            yield frame, current_time, original_fps
            
            frame_count += 1
            current_time = frame_count / original_fps
    
    finally:
        cap.release()
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def create_video_from_frames(frames: list, output_path: str, fps: float = 30.0, width: int = None, height: int = None):
    """
    Create a video file from a list of frames.
    
    Args:
        frames: List of numpy arrays (BGR format)
        output_path: Path to save video
        fps: Frames per second
        width: Video width (uses first frame if None)
        height: Video height (uses first frame if None)
    """
    if not frames:
        raise ValueError("No frames provided")
    
    # Get dimensions from first frame
    h, w = frames[0].shape[:2]
    width = width or w
    height = height or h
    
    # Try different codecs for better compatibility
    # H.264 codec (avc1) is most compatible
    codecs_to_try = [
        ('avc1', 'H.264/AVC'),
        ('mp4v', 'MPEG-4'),
        ('XVID', 'XVID'),
    ]
    
    out = None
    for fourcc_str, codec_name in codecs_to_try:
        try:
            fourcc = cv2.VideoWriter_fourcc(*fourcc_str)
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            if out.isOpened():
                print(f"Using codec: {codec_name} ({fourcc_str})")
                break
            else:
                out.release()
                out = None
        except Exception as e:
            if out:
                out.release()
                out = None
            continue
    
    if out is None or not out.isOpened():
        raise ValueError("Failed to create video writer with any codec")
    
    try:
        for frame in frames:
            # Ensure frame is in correct format
            if len(frame.shape) == 2:
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            elif frame.shape[2] == 4:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            
            # Resize if needed
            if frame.shape[1] != width or frame.shape[0] != height:
                frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_LINEAR)
            
            # Ensure frame is uint8
            if frame.dtype != np.uint8:
                frame = np.clip(frame, 0, 255).astype(np.uint8)
            
            out.write(frame)
    finally:
        out.release()
