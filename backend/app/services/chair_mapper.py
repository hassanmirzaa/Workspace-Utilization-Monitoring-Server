"""
Chair-Person association logic.
"""
from typing import List, Dict, Optional, Tuple
from app.config import (
    PERSON_CHAIR_OVERLAP_THRESHOLD,
    PERSON_CHAIR_CENTROID_DISTANCE_THRESHOLD
)
from app.services.detector import YOLODetector


class ChairMapper:
    """Maps persons to chairs based on spatial relationships."""
    
    def __init__(self, detector: YOLODetector):
        """
        Initialize ChairMapper.
        
        Args:
            detector: YOLODetector instance for utility methods
        """
        self.detector = detector
    
    def get_centroid(self, bbox: List[float]) -> Tuple[float, float]:
        """Calculate centroid of bounding box."""
        x1, y1, x2, y2 = bbox
        return ((x1 + x2) / 2, (y1 + y2) / 2)
    
    def calculate_distance(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two points."""
        return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5
    
    def associate_person_to_chair(
        self,
        person_bbox: List[float],
        chair_bbox: List[float]
    ) -> bool:
        """
        Determine if a person is associated with a chair.
        
        A person is considered sitting on a chair if:
        1. Person bounding box overlaps chair bounding box (IoU > threshold)
        OR
        2. Person centroid is above chair centroid (within distance threshold)
        
        Args:
            person_bbox: Person bounding box [x1, y1, x2, y2]
            chair_bbox: Chair bounding box [x1, y1, x2, y2]
            
        Returns:
            True if person is associated with chair
        """
        # Method 1: Check IoU overlap
        iou = self.detector.calculate_iou(person_bbox, chair_bbox)
        if iou >= PERSON_CHAIR_OVERLAP_THRESHOLD:
            return True
        
        # Method 2: Check centroid distance and vertical relationship
        person_centroid = self.get_centroid(person_bbox)
        chair_centroid = self.get_centroid(chair_bbox)
        
        # Person should be above chair (person_y < chair_y typically)
        # But we allow some flexibility
        distance = self.calculate_distance(person_centroid, chair_centroid)
        
        if distance <= PERSON_CHAIR_CENTROID_DISTANCE_THRESHOLD:
            # Check if person is roughly above chair (within reasonable vertical range)
            vertical_diff = person_centroid[1] - chair_centroid[1]
            # Allow person to be slightly above or overlapping vertically
            if vertical_diff <= chair_bbox[3] - chair_bbox[1]:  # Within chair height
                return True
        
        return False
    
    def map_chairs_to_persons(
        self,
        chairs: List[Dict],
        persons: List[Dict]
    ) -> Dict[str, Optional[Dict]]:
        """
        Map each chair to an associated person (if any).
        
        Args:
            chairs: List of chair detections with 'bbox' and 'confidence'
            persons: List of person detections with 'bbox' and 'confidence'
            
        Returns:
            Dictionary mapping chair_id to person detection (or None)
        """
        mapping = {}
        
        for idx, chair in enumerate(chairs):
            chair_id = f"chair_{idx + 1}"
            best_person = None
            best_overlap = 0.0
            
            # Find best matching person for this chair
            for person in persons:
                if self.associate_person_to_chair(person['bbox'], chair['bbox']):
                    # Use IoU as quality metric
                    overlap = self.detector.calculate_iou(person['bbox'], chair['bbox'])
                    if overlap > best_overlap:
                        best_overlap = overlap
                        best_person = person
            
            mapping[chair_id] = best_person
        
        return mapping
