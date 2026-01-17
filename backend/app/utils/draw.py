"""
Drawing utilities for visualizing detections and statuses.
"""
import cv2
import numpy as np
from typing import List, Tuple
from app.config import STATUS_COLORS


def draw_bbox(
    image: np.ndarray,
    bbox: List[float],
    color: Tuple[int, int, int],
    thickness: int = 2,
    label: str = None
) -> np.ndarray:
    """
    Draw a bounding box on the image.
    
    Args:
        image: Image array (BGR format)
        bbox: Bounding box [x1, y1, x2, y2]
        color: BGR color tuple
        thickness: Line thickness
        label: Optional label text
        
    Returns:
        Image with drawn bounding box
    """
    x1, y1, x2, y2 = map(int, bbox)
    
    # Draw rectangle
    cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)
    
    # Draw label if provided
    if label:
        # Calculate text size
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        text_thickness = 2
        (text_width, text_height), baseline = cv2.getTextSize(label, font, font_scale, text_thickness)
        
        # Draw background rectangle for text
        cv2.rectangle(
            image,
            (x1, y1 - text_height - baseline - 5),
            (x1 + text_width, y1),
            color,
            -1
        )
        
        # Draw text
        cv2.putText(
            image,
            label,
            (x1, y1 - baseline - 2),
            font,
            font_scale,
            (255, 255, 255),  # White text
            text_thickness,
            cv2.LINE_AA
        )
    
    return image


def draw_chair_status(
    image: np.ndarray,
    chair_id: str,
    status: str,
    bbox: List[float],
    confidence: float
) -> np.ndarray:
    """
    Draw a chair with its status color and label.
    
    Args:
        image: Image array (BGR format)
        chair_id: Chair identifier
        status: Status (RED, ORANGE, GREEN)
        bbox: Bounding box [x1, y1, x2, y2]
        confidence: Confidence score
        
    Returns:
        Image with drawn chair status
    """
    color = STATUS_COLORS.get(status, (255, 255, 255))
    label = f"{chair_id}: {status} ({confidence:.2f})"
    
    return draw_bbox(image, bbox, color, thickness=3, label=label)


def draw_all_chairs(
    image: np.ndarray,
    chairs: List[dict]
) -> np.ndarray:
    """
    Draw all chairs with their statuses on the image.
    
    Args:
        image: Image array (BGR format)
        chairs: List of chair dictionaries with chair_id, status, bbox, confidence
        
    Returns:
        Annotated image
    """
    annotated = image.copy()
    
    for chair in chairs:
        annotated = draw_chair_status(
            annotated,
            chair["chair_id"],
            chair["status"],
            chair["bbox"],
            chair["confidence"]
        )
    
    return annotated
