"""
MediaPipe hand detection service.
"""
import os
import sys
import warnings
from typing import List, Tuple, Optional, Dict

# Workaround for MediaPipe 0.10.7 TensorFlow/protobuf conflict
# MediaPipe tries to import tensorflow.tools.docs.doc_controls as an optional dependency
# We create a dummy module to prevent the import error
if 'tensorflow' not in sys.modules:
    try:
        # Create a proper doc_controls class that mimics TensorFlow's decorator
        class DocControls:
            """Dummy doc_controls class to replace TensorFlow's doc_controls."""
            @staticmethod
            def do_not_generate_docs(func):
                """Decorator that does nothing."""
                return func
            
            @staticmethod
            def do_not_doc_in_subclasses(func):
                """Decorator that does nothing."""
                return func
            
            def __call__(self, *args, **kwargs):
                """Allow doc_controls to be called as a function."""
                if args and callable(args[0]):
                    return args[0]
                return lambda x: x
        
        # Create minimal dummy TensorFlow module structure
        class DummyModule:
            pass
        
        tf_dummy = DummyModule()
        tf_dummy.tools = DummyModule()
        tf_dummy.tools.docs = DummyModule()
        tf_dummy.tools.docs.doc_controls = DocControls()
        
        # Register in sys.modules before MediaPipe tries to import
        sys.modules['tensorflow'] = tf_dummy
        sys.modules['tensorflow.tools'] = tf_dummy.tools
        sys.modules['tensorflow.tools.docs'] = tf_dummy.tools.docs
    except Exception as e:
        # If workaround fails, user needs to uninstall TensorFlow
        print(f"Warning: Could not create TensorFlow dummy module: {e}")
        print("If MediaPipe import fails, try: pip uninstall tensorflow")

# Suppress warnings during import
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import numpy as np
    import cv2
    
    try:
        import mediapipe as mp
    except ImportError as e:
        if 'protobuf' in str(e).lower() or 'tensorflow' in str(e).lower():
            raise ImportError(
                "MediaPipe import failed due to protobuf/TensorFlow conflict. "
                "Solution: pip uninstall tensorflow\n"
                f"Original error: {e}"
            )
        raise
from app.config import (
    MEDIAPIPE_HANDS_MODEL_COMPLEXITY,
    MEDIAPIPE_MAX_NUM_HANDS,
    MEDIAPIPE_MIN_DETECTION_CONFIDENCE,
    MEDIAPIPE_MIN_TRACKING_CONFIDENCE,
    HAND_TABLE_INTERSECTION_THRESHOLD,
    HAND_TABLE_PROXIMITY_THRESHOLD
)


class HandDetector:
    """MediaPipe hand detection for detecting hands and keypoints."""
    
    def __init__(self):
        """Initialize MediaPipe Hands."""
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=MEDIAPIPE_MAX_NUM_HANDS,
            model_complexity=MEDIAPIPE_HANDS_MODEL_COMPLEXITY,
            min_detection_confidence=MEDIAPIPE_MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=MEDIAPIPE_MIN_TRACKING_CONFIDENCE
        )
        self.mp_drawing = mp.solutions.drawing_utils
        print("MediaPipe Hands initialized")
    
    def detect_hands(self, image: np.ndarray) -> List[Dict]:
        """
        Detect hands and their keypoints in the image.
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            List of hand detections, each containing:
            {
                'landmarks': List of (x, y) tuples (normalized 0-1),
                'keypoints': List of (x, y) tuples (pixel coordinates),
                'confidence': float
            }
        """
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Process image
        results = self.hands.process(rgb_image)
        
        hands_data = []
        
        if results.multi_hand_landmarks:
            h, w = image.shape[:2]
            
            for hand_landmarks in results.multi_hand_landmarks:
                # Extract landmarks (normalized coordinates)
                landmarks = []
                keypoints = []
                
                for landmark in hand_landmarks.landmark:
                    # Normalized coordinates
                    landmarks.append((landmark.x, landmark.y))
                    # Pixel coordinates
                    keypoints.append((int(landmark.x * w), int(landmark.y * h)))
                
                # Get hand confidence (if available)
                confidence = 1.0  # MediaPipe doesn't provide per-hand confidence
                
                hands_data.append({
                    'landmarks': landmarks,
                    'keypoints': keypoints,
                    'confidence': confidence
                })
        
        return hands_data
    
    def is_hand_on_table(
        self,
        hand_keypoints: List[Tuple[float, float]],
        table_bbox: List[float],
        threshold: float = None
    ) -> bool:
        """
        Check if hand keypoints intersect with table bounding box.
        Improved for laptop/desk work scenarios.
        
        Args:
            hand_keypoints: List of (x, y) pixel coordinates
            table_bbox: Table bounding box [x1, y1, x2, y2]
            threshold: Minimum fraction of keypoints that must be in/on table (uses config if None)
            
        Returns:
            True if hand is considered on table
        """
        if not hand_keypoints or not table_bbox:
            return False
        
        if threshold is None:
            threshold = HAND_TABLE_INTERSECTION_THRESHOLD
        
        x1, y1, x2, y2 = table_bbox
        
        # Expand table bbox slightly for proximity check (helps with laptop work)
        # Hands working on laptop are often slightly above or near the table surface
        proximity_margin = HAND_TABLE_PROXIMITY_THRESHOLD
        expanded_x1 = x1 - proximity_margin
        expanded_y1 = y1 - proximity_margin  # Allow hands slightly above table
        expanded_x2 = x2 + proximity_margin
        expanded_y2 = y2 + proximity_margin
        
        # Focus on wrist and finger tips (indices: 0=wrist, 4=thumb, 8=index, 12=middle, 16=ring, 20=pinky)
        important_indices = [0, 4, 8, 12, 16, 20]
        
        points_inside = 0
        points_near = 0
        
        for idx in important_indices:
            if idx < len(hand_keypoints):
                x, y = hand_keypoints[idx]
                
                # Check if inside table bbox
                if x1 <= x <= x2 and y1 <= y <= y2:
                    points_inside += 1
                    points_near += 1
                # Check if near table (expanded bbox) - for laptop/desk work
                elif expanded_x1 <= x <= expanded_x2 and expanded_y1 <= y <= expanded_y2:
                    points_near += 1
        
        # More lenient check: if enough keypoints are inside OR near table
        if len(important_indices) > 0:
            fraction_inside = points_inside / len(important_indices)
            fraction_near = points_near / len(important_indices)
            
            # If at least threshold fraction are inside, definitely on table
            if fraction_inside >= threshold:
                return True
            
            # If many keypoints are near table (for laptop work), also consider on table
            # This handles cases where hands are on keyboard/mouse slightly above table surface
            if fraction_near >= (threshold + 0.2):  # More lenient for proximity
                return True
            
            # Special case: if wrist and at least 2 finger tips are near/on table
            # This handles laptop typing scenarios
            wrist_idx = 0
            finger_tip_indices = [4, 8, 12, 16, 20]  # Thumb, index, middle, ring, pinky
            
            if wrist_idx < len(hand_keypoints):
                wx, wy = hand_keypoints[wrist_idx]
                wrist_near = (expanded_x1 <= wx <= expanded_x2 and expanded_y1 <= wy <= expanded_y2)
                
                finger_tips_near = 0
                for tip_idx in finger_tip_indices:
                    if tip_idx < len(hand_keypoints):
                        tx, ty = hand_keypoints[tip_idx]
                        if expanded_x1 <= tx <= expanded_x2 and expanded_y1 <= ty <= expanded_y2:
                            finger_tips_near += 1
                
                # If wrist is near table and at least 2 finger tips are near, consider hands on table
                if wrist_near and finger_tips_near >= 2:
                    return True
        
        return False
    
    def are_hands_on_table(
        self,
        hands: List[Dict],
        table_bbox: Optional[List[float]],
        person_bbox: Optional[List[float]] = None
    ) -> bool:
        """
        Check if any detected hands are on the table.
        If no table is detected, uses fallback logic for laptop/desk work.
        
        Args:
            hands: List of hand detections
            table_bbox: Table bounding box [x1, y1, x2, y2] or None
            person_bbox: Person bounding box [x1, y1, x2, y2] for fallback logic
            
        Returns:
            True if at least one hand is on table or in working position
        """
        if not hands:
            return False
        
        # If table is detected, use table-based detection
        if table_bbox:
            for hand in hands:
                keypoints = hand.get('keypoints', [])
                if self.is_hand_on_table(keypoints, table_bbox):
                    return True
        
        # Fallback: If no table detected but hands are present and person is detected
        # Check if hands are in a "working position" (lower part of person, in front)
        if not table_bbox and person_bbox and hands:
            return self._are_hands_in_working_position(hands, person_bbox)
        
        return False
    
    def _are_hands_in_working_position(
        self,
        hands: List[Dict],
        person_bbox: List[float]
    ) -> bool:
        """
        Fallback: Check if hands are in a working position relative to person.
        For laptop/desk work when table is not detected.
        
        Args:
            hands: List of hand detections
            person_bbox: Person bounding box [x1, y1, x2, y2]
            
        Returns:
            True if hands appear to be in working position
        """
        if not hands or not person_bbox:
            return False
        
        px1, py1, px2, py2 = person_bbox
        person_center_x = (px1 + px2) / 2
        person_center_y = (py1 + py2) / 2
        person_width = px2 - px1
        person_height = py2 - py1
        
        # Define working area: lower 60% of person, horizontally centered with some margin
        working_area_x1 = px1 - person_width * 0.3  # Extend slightly left
        working_area_x2 = px2 + person_width * 0.3  # Extend slightly right
        working_area_y1 = py1 + person_height * 0.4  # Lower 60% of person
        working_area_y2 = py2 + person_height * 0.2  # Slightly below person
        
        for hand in hands:
            keypoints = hand.get('keypoints', [])
            if not keypoints:
                continue
            
            # Check wrist and finger tips
            important_indices = [0, 4, 8, 12, 16, 20]  # wrist, thumb, index, middle, ring, pinky
            points_in_working_area = 0
            
            for idx in important_indices:
                if idx < len(keypoints):
                    x, y = keypoints[idx]
                    if (working_area_x1 <= x <= working_area_x2 and 
                        working_area_y1 <= y <= working_area_y2):
                        points_in_working_area += 1
            
            # If at least 3 keypoints are in working area, consider hands working
            if points_in_working_area >= 3:
                return True
        
        return False
