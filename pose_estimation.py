import cv2
import mediapipe as mp
import logging

# Suppress Mediapipe warnings
logging.getLogger('mediapipe').setLevel(logging.ERROR)

class PoseEstimation:
    def __init__(self):
        """Initialize Mediapipe Pose and Hands models."""
        self.mp_pose = mp.solutions.pose
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5)
        self.hands = self.mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5)
        # Track hand position for gesture detection
        self.prev_hand_x = None
        self.wave_counter = 0
        self.is_waving = False
    
    def process_frame(self, frame):
        """Process a frame to detect poses, hands, and gestures."""
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pose_results = self.pose.process(frame_rgb)
        hand_results = self.hands.process(frame_rgb)
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        
        # Draw pose landmarks
        if pose_results.pose_landmarks:
            self.mp_drawing.draw_landmarks(frame_bgr, pose_results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
        
        # Draw hand landmarks and detect waving
        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(frame_bgr, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                # Use wrist (landmark 0) to detect waving
                wrist_x = hand_landmarks.landmark[0].x
                if self.prev_hand_x is not None:
                    # Detect rapid left-right movement
                    if abs(wrist_x - self.prev_hand_x) > 0.05:  # Threshold for movement
                        self.wave_counter += 1
                        if self.wave_counter > 5:  # Number of rapid movements to consider a wave
                            self.is_waving = not self.is_waving  # Toggle waving state
                            self.wave_counter = 0
                self.prev_hand_x = wrist_x
        
        return frame_bgr, pose_results, {'is_waving': self.is_waving}
    
    def get_landmarks(self, results):
        """Extract coordinates for specific landmarks."""
        if not results.pose_landmarks:
            return {}
        landmarks = {
            'right_wrist': results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_WRIST],
            'left_wrist': results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_WRIST],
            'head': results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.NOSE]
        }
        return landmarks