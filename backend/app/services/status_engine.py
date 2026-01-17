"""
Status engine for determining RED/ORANGE/GREEN status per chair.
"""
from typing import List, Dict, Optional, Tuple
from app.services.chair_mapper import ChairMapper
from app.services.pose import HandDetector


class StatusEngine:
    """Core logic for determining chair activity status."""
    
    def __init__(self, chair_mapper: ChairMapper, hand_detector: HandDetector):
        """
        Initialize StatusEngine.
        
        Args:
            chair_mapper: ChairMapper instance
            hand_detector: HandDetector instance
        """
        self.chair_mapper = chair_mapper
        self.hand_detector = hand_detector
    
    def determine_status(
        self,
        chair_id: str,
        chair_bbox: List[float],
        associated_person: Optional[Dict],
        hands: List[Dict],
        table_bbox: Optional[List[float]]
    ) -> Tuple[str, float]:
        """
        Determine status for a single chair.
        
        Logic:
        - IF no person on chair: RED
        - ELSE IF hands on table: GREEN
        - ELSE: ORANGE
        
        Args:
            chair_id: Chair identifier
            chair_bbox: Chair bounding box
            associated_person: Associated person detection or None
            hands: List of detected hands
            table_bbox: Table bounding box or None
            
        Returns:
            Tuple of (status, confidence)
            status: "RED", "ORANGE", or "GREEN"
            confidence: Confidence score (0.0 to 1.0)
        """
        # Step 1: Check if person is sitting
        if associated_person is None:
            return ("RED", 1.0)  # High confidence for empty chair
        
        # Step 2: Check if hands are on table
        hands_on_table = self.hand_detector.are_hands_on_table(hands, table_bbox)
        
        if hands_on_table:
            return ("GREEN", 0.9)  # Person sitting with hands on table
        else:
            return ("ORANGE", 0.85)  # Person sitting but hands not on table
    
    def process_frame(
        self,
        chairs: List[Dict],
        persons: List[Dict],
        tables: List[Dict],
        hands: List[Dict]
    ) -> List[Dict]:
        """
        Process a frame and determine status for all chairs.
        
        Args:
            chairs: List of chair detections
            persons: List of person detections
            tables: List of table detections
            hands: List of hand detections
            
        Returns:
            List of chair results with:
            {
                'chair_id': str,
                'status': str,
                'confidence': float,
                'bbox': List[float]
            }
        """
        # Map chairs to persons
        chair_person_mapping = self.chair_mapper.map_chairs_to_persons(chairs, persons)
        
        results = []
        
        for idx, chair in enumerate(chairs):
            chair_id = f"chair_{idx + 1}"
            associated_person = chair_person_mapping.get(chair_id)
            
            # Find the table closest to this chair/person
            table_bbox = self._find_closest_table(chair, associated_person, tables)
            
            # Determine status
            status, confidence = self.determine_status(
                chair_id,
                chair['bbox'],
                associated_person,
                hands,
                table_bbox
            )
            
            # Combine with chair confidence
            final_confidence = min(confidence, chair.get('confidence', 0.5))
            
            results.append({
                'chair_id': chair_id,
                'status': status,
                'confidence': final_confidence,
                'bbox': chair['bbox']
            })
        
        return results
    
    def _find_closest_table(
        self,
        chair: Dict,
        person: Optional[Dict],
        tables: List[Dict]
    ) -> Optional[List[float]]:
        """
        Find the table closest to the chair or person.
        
        Args:
            chair: Chair detection dict
            person: Person detection dict or None
            tables: List of table detections
            
        Returns:
            Table bounding box closest to chair/person, or None
        """
        if not tables:
            return None
        
        if len(tables) == 1:
            return tables[0]['bbox']
        
        # Use person position if available, otherwise use chair position
        if person:
            ref_bbox = person['bbox']
        else:
            ref_bbox = chair['bbox']
        
        # Calculate center of reference bbox
        ref_center = (
            (ref_bbox[0] + ref_bbox[2]) / 2,
            (ref_bbox[1] + ref_bbox[3]) / 2
        )
        
        # Find closest table
        closest_table = None
        min_distance = float('inf')
        
        for table in tables:
            table_bbox = table['bbox']
            table_center = (
                (table_bbox[0] + table_bbox[2]) / 2,
                (table_bbox[1] + table_bbox[3]) / 2
            )
            
            # Calculate distance
            distance = ((ref_center[0] - table_center[0]) ** 2 + 
                       (ref_center[1] - table_center[1]) ** 2) ** 0.5
            
            if distance < min_distance:
                min_distance = distance
                closest_table = table_bbox
        
        return closest_table