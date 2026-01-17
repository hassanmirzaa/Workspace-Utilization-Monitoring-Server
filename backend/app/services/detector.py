"""
YOLOv8 object detection service.
"""
import os
import numpy as np
from typing import List, Dict, Tuple

# Fix for PyTorch 2.6+ weights_only issue
# Set environment variable before importing YOLO
os.environ.setdefault('TORCH_LOAD_WEIGHTS_ONLY', 'False')

# Monkey-patch torch.load to allow loading YOLO models
try:
    import torch
    _original_load = torch.load
    
    def _patched_load(*args, **kwargs):
        """Patched torch.load to allow loading YOLO models."""
        if 'weights_only' not in kwargs:
            kwargs['weights_only'] = False
        return _original_load(*args, **kwargs)
    
    torch.load = _patched_load
except ImportError:
    pass  # torch not available, will fail later anyway

from ultralytics import YOLO
from app.config import (
    YOLO_MODEL_PATH,
    YOLO_CONFIDENCE_THRESHOLD,
    YOLO_IOU_THRESHOLD,
    CLASS_ID_CHAIR,
    CLASS_ID_PERSON,
    CLASS_ID_TABLE,
    DEVICE
)


class YOLODetector:
    """YOLOv8 detector for chairs, persons, and tables."""
    
    def __init__(self):
        """Initialize YOLO model."""
        self.model = YOLO(YOLO_MODEL_PATH)
        self.model.to(DEVICE)
        print(f"YOLO model loaded on device: {DEVICE}")
    
    def detect(self, image: np.ndarray) -> Dict[str, List[Dict]]:
        """
        Detect chairs, persons, and tables in the image.
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            Dictionary with keys: 'chairs', 'persons', 'tables'
            Each value is a list of detections with:
            {
                'bbox': [x1, y1, x2, y2],
                'confidence': float,
                'class_id': int
            }
        """
        # Run inference
        results = self.model(
            image,
            conf=YOLO_CONFIDENCE_THRESHOLD,
            iou=YOLO_IOU_THRESHOLD,
            verbose=False
        )
        
        detections = {
            'chairs': [],
            'persons': [],
            'tables': []
        }
        
        if len(results) == 0:
            return detections
        
        result = results[0]
        
        # Extract boxes, scores, and class IDs
        boxes = result.boxes
        if boxes is None or len(boxes) == 0:
            return detections
        
        for box in boxes:
            # Get box coordinates (xyxy format)
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            confidence = float(box.conf[0].cpu().numpy())
            class_id = int(box.cls[0].cpu().numpy())
            
            bbox = [float(x1), float(y1), float(x2), float(y2)]
            
            detection = {
                'bbox': bbox,
                'confidence': confidence,
                'class_id': class_id
            }
            
            # Categorize by class ID
            if class_id == CLASS_ID_CHAIR:
                detections['chairs'].append(detection)
            elif class_id == CLASS_ID_PERSON:
                detections['persons'].append(detection)
            elif class_id == CLASS_ID_TABLE:
                detections['tables'].append(detection)
        
        return detections
    
    def get_bbox_center(self, bbox: List[float]) -> Tuple[float, float]:
        """Calculate center point of bounding box."""
        x1, y1, x2, y2 = bbox
        return ((x1 + x2) / 2, (y1 + y2) / 2)
    
    def calculate_iou(self, bbox1: List[float], bbox2: List[float]) -> float:
        """
        Calculate Intersection over Union (IoU) between two bounding boxes.
        
        Args:
            bbox1: [x1, y1, x2, y2]
            bbox2: [x1, y1, x2, y2]
            
        Returns:
            IoU value between 0 and 1
        """
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        # Calculate intersection
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)
        
        if x2_i <= x1_i or y2_i <= y1_i:
            return 0.0
        
        intersection = (x2_i - x1_i) * (y2_i - y1_i)
        
        # Calculate union
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        union = area1 + area2 - intersection
        
        if union == 0:
            return 0.0
        
        return intersection / union
