"""
Image processing utilities for frame encoding/decoding.
"""
import io
import numpy as np
import cv2
from PIL import Image
from typing import Tuple, Optional
from app.config import MAX_IMAGE_SIZE, JPEG_QUALITY


def decode_image(image_bytes: bytes) -> np.ndarray:
    """
    Decode JPEG/PNG image bytes to numpy array (BGR format).
    
    Args:
        image_bytes: Raw image bytes
        
    Returns:
        numpy array in BGR format (OpenCV format)
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image is None:
        raise ValueError("Failed to decode image. Ensure valid JPEG/PNG format.")
    
    # Resize if too large
    h, w = image.shape[:2]
    max_w, max_h = MAX_IMAGE_SIZE
    if w > max_w or h > max_h:
        scale = min(max_w / w, max_h / h)
        new_w, new_h = int(w * scale), int(h * scale)
        image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    
    return image


def encode_image(image: np.ndarray, format: str = "JPEG") -> bytes:
    """
    Encode numpy array (BGR format) to image bytes.
    
    Args:
        image: numpy array in BGR format
        format: Output format ("JPEG" or "PNG")
        
    Returns:
        Encoded image bytes
    """
    if format.upper() == "JPEG":
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY]
        success, encoded_image = cv2.imencode('.jpg', image, encode_param)
    elif format.upper() == "PNG":
        success, encoded_image = cv2.imencode('.png', image)
    else:
        raise ValueError(f"Unsupported format: {format}")
    
    if not success:
        raise ValueError(f"Failed to encode image as {format}")
    
    return encoded_image.tobytes()


def bgr_to_rgb(image: np.ndarray) -> np.ndarray:
    """Convert BGR to RGB."""
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def rgb_to_bgr(image: np.ndarray) -> np.ndarray:
    """Convert RGB to BGR."""
    return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
