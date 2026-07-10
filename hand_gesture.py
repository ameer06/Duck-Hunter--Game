# Hand Gesture Detection for Duck Hunter
# Detects finger gun pose and shooting motion
# Uses MediaPipe for hand tracking

import cv2
import numpy as np
from collections import deque
import time
import mediapipe as mp

class HandGestureDetector:
    # handles all the hand tracking stuff
    
    def __init__(self):
        """Initialize MediaPipe hands detector"""
        
        # Initialize MediaPipe
        self.mp_hands = mp.solutions.hands if hasattr(mp, 'solutions') else None
        self.mp_draw = mp.solutions.drawing_utils if hasattr(mp, 'solutions') else None
        
        # Try to initialize hands detector
        self.hands = None
        self.detector_working = False
        
        if self.mp_hands:
            try:
                # Use legacy solutions API (works with older MediaPipe)
                self.hands = self.mp_hands.Hands(
                    static_image_mode=False,
                    max_num_hands=1,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5
                )
                self.detector_working = True
                print("✓ Using MediaPipe Hands (solutions API)")
            except Exception as e:
                print(f"⚠ MediaPipe solutions API failed: {e}")
        
        # If solutions didn't work, try new tasks API
        if not self.detector_working:
            try:
                # Download and use hand landmarker model
                import urllib.request
                import os
                
                model_path = 'hand_landmarker.task'
                if not os.path.exists(model_path):
                    print("Downloading hand detection model...")
                    url = 'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task'
                    urllib.request.urlretrieve(url, model_path)
                    print("✓ Model downloaded")
                
                BaseOptions = mp.tasks.BaseOptions
                HandLandmarker = mp.tasks.vision.HandLandmarker
                HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
                VisionRunningMode = mp.tasks.vision.RunningMode
                
                options = HandLandmarkerOptions(
                    base_options=BaseOptions(model_asset_path=model_path),
                    running_mode=VisionRunningMode.VIDEO,
                    num_hands=1
                )
                
                self.hands = HandLandmarker.create_from_options(options)
                self.detector_working = True
                self.use_new_api = True
                print("✓ Using MediaPipe Hands (tasks API)")
            except Exception as e:
                print(f"⚠ MediaPipe tasks API failed: {e}")
                print("⚠ Hand detection disabled")
                self.use_new_api = False
        else:
            self.use_new_api = False
        
        # Finger landmark indices
        self.FINGER_TIPS = {
            'thumb': 4,
            'index': 8,
            'middle': 12,
            'ring': 16,
            'pinky': 20
        }
        
        # Trigger detection
        self.thumb_history = deque(maxlen=5)  # track thumb movement
        self.last_shot_time = 0
        self.cooldown_ms = 300  # wait 300ms between shots
        
        self.frame_count = 0  # for video mode
        
    def process_frame(self, frame):
        """Process camera frame and detect hand landmarks"""
        if not self.detector_working or self.hands is None:
            return frame, None
        
        try:
            if self.use_new_api:
                # New tasks API
                self.frame_count += 1
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
                
                # Detect with timestamp
                result = self.hands.detect_for_video(mp_image, self.frame_count)
                
                if result.hand_landmarks:
                    # Draw landmarks manually
                    for hand_landmarks in result.hand_landmarks:
                        # Convert to format for drawing
                        self.draw_landmarks_manual(frame, hand_landmarks)
                        return frame, hand_landmarks
                return frame, None
            else:
                # Old solutions API
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.hands.process(rgb_frame)
                
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        if self.mp_draw:
                            self.mp_draw.draw_landmarks(
                                frame,
                                hand_landmarks,
                                self.mp_hands.HAND_CONNECTIONS
                            )
                        return frame, hand_landmarks
                return frame, None
        except Exception as e:
            print(f"Error in hand detection: {e}")
            return frame, None
    
    def draw_landmarks_manual(self, frame, landmarks):
        """Draw hand landmarks manually"""
        h, w, _ = frame.shape
        
        # Draw landmarks as circles
        for i, landmark in enumerate(landmarks):
            if hasattr(landmark, 'x'):
                x, y = int(landmark.x * w), int(landmark.y * h)
            else:
                x, y = int(landmark[0] * w), int(landmark[1] * h)
            cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
    
    def get_landmark_value(self, landmarks, index, attr):
        """Get landmark attribute value (handles both API formats)"""
        if hasattr(landmarks, 'landmark'):
            # Old API
            landmark = landmarks.landmark[index]
            return getattr(landmark, attr)
        else:
            # New API (list of landmarks)
            landmark = landmarks[index]
            if hasattr(landmark, attr):
                return getattr(landmark, attr)
            else:
                # It's a list/tuple [x, y, z]
                if attr == 'x':
                    return landmark[0] if hasattr(landmark, '__getitem__') else landmark.x
                elif attr == 'y':
                    return landmark[1] if hasattr(landmark, '__getitem__') else landmark.y
                elif attr == 'z':
                    return landmark[2] if hasattr(landmark, '__getitem__') else landmark.z
    
    def is_finger_extended(self, landmarks, finger_name):
        """Check if a finger is extended"""
        try:
            if finger_name == 'thumb':
                thumb_tip_y = self.get_landmark_value(landmarks, 4, 'y')
                thumb_base_y = self.get_landmark_value(landmarks, 2, 'y')
                return thumb_tip_y < thumb_base_y - 0.05
            else:
                # For other fingers
                tip_idx = self.FINGER_TIPS[finger_name]
                base_idx = tip_idx - 3
                
                tip_y = self.get_landmark_value(landmarks, tip_idx, 'y')
                base_y = self.get_landmark_value(landmarks, base_idx, 'y')
                
                return tip_y < base_y
        except Exception as e:
            return False
    
    def is_finger_gun(self, landmarks):
        """Validate finger gun pose"""
        if not landmarks:
            return False
        
        try:
            index_up = self.is_finger_extended(landmarks, 'index')
            thumb_up = self.is_finger_extended(landmarks, 'thumb')
            middle_down = not self.is_finger_extended(landmarks, 'middle')
            ring_down = not self.is_finger_extended(landmarks, 'ring')
            pinky_down = not self.is_finger_extended(landmarks, 'pinky')
            
            return all([index_up, thumb_up, middle_down, ring_down, pinky_down])
        except Exception as e:
            return False
    
    def detect_trigger_pull(self, landmarks):
        """Detect thumb motion for trigger"""
        if not landmarks:
            return False
        
        current_time = time.time() * 1000
        
        if current_time - self.last_shot_time < self.cooldown_ms:
            return False
        
        try:
            thumb_y = self.get_landmark_value(landmarks, 4, 'y')
            self.thumb_history.append(thumb_y)
            
            if len(self.thumb_history) < 5:
                return False
            
            positions = list(self.thumb_history)
            
            # Detect valley pattern
            if positions[2] > positions[0] + 0.01 and positions[2] > positions[4] + 0.01:
                motion = abs(positions[0] - positions[4])
                
                if motion > 0.03:
                    self.last_shot_time = current_time
                    self.thumb_history.clear()
                    return True
        except Exception as e:
            pass
        
        return False
    
    def get_aim_position(self, landmarks, frame_width, frame_height):
        """Get crosshair position from index fingertip"""
        if not landmarks:
            return None
        
        try:
            index_x = self.get_landmark_value(landmarks, 8, 'x')
            index_y = self.get_landmark_value(landmarks, 8, 'y')
            
            # Convert to screen coordinates (NO flip - frame is already mirrored in main.py)
            x = int(index_x * frame_width)
            y = int(index_y * frame_height)
            
            # Clamp to bounds
            x = max(0, min(frame_width, x))
            y = max(0, min(frame_height, y))
            
            return (x, y)
        except Exception as e:
            return None
    
    def update(self, frame, game_width, game_height):
        """Main update function"""
        debug_frame, landmarks = self.process_frame(frame)
        
        result = {
            'aim_pos': None,
            'is_finger_gun': False,
            'trigger_pulled': False,
            'debug_frame': debug_frame
        }
        
        if landmarks:
            result['is_finger_gun'] = self.is_finger_gun(landmarks)
            
            if result['is_finger_gun']:
                result['aim_pos'] = self.get_aim_position(landmarks, game_width, game_height)
                result['trigger_pulled'] = self.detect_trigger_pull(landmarks)
            else:
                self.thumb_history.clear()
        
        return result
    
    def close(self):
        """Cleanup"""
        if self.hands:
            try:
                self.hands.close()
            except Exception:
                pass
