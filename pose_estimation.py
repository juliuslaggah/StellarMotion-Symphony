import cv2
import mediapipe as mp
import logging

# Suppress Mediapipe warnings
logging.getLogger('mediapipe').setLevel(logging.ERROR)

class PoseEstimation:
    def __init__(self):
        """Initialize Mediapipe Pose and Hands models, plus gesture state."""
        self.mp_pose = mp.solutions.pose
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils

        # Pose model
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            min_detection_confidence=0.5
        )
        # Hands model
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5
        )

        # Existing wave‐detection state
        self.prev_hand_x = None
        self.wave_counter = 0
        self.is_waving = False

        # New gesture flags
        self.is_thumbs_up = False
        self.is_peace_sign = False
        self.is_clapping = False

        # (Optional) keep previous states if you want a one‐shot trigger
        self.prev_thumbs_up = False
        self.prev_peace_sign = False
        self.prev_clapping = False

    def process_frame(self, frame):
        """Process a frame to detect pose, hands, and all gestures."""
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pose_results = self.pose.process(frame_rgb)
        hand_results = self.hands.process(frame_rgb)
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

        # Draw pose landmarks
        if pose_results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                frame_bgr,
                pose_results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS
            )

        # Reset gesture flags each frame
        self.is_thumbs_up = False
        self.is_peace_sign = False
        self.is_clapping = False

        # If any hand landmarks detected:
        if hand_results.multi_hand_landmarks:
            hands_list = hand_results.multi_hand_landmarks

            # 1) Detect clap if exactly two hands are present
            if len(hands_list) == 2:
                current_clap = self._is_clapping(hands_list)
                # If you want a one‐shot clap trigger:
                if current_clap and not self.prev_clapping:
                    self.is_clapping = True
                # Or to keep it “true” while hands are together:
                # self.is_clapping = current_clap
                self.prev_clapping = current_clap

            # 2) For each hand, draw landmarks & detect wave, thumbs-up, peace sign
            for hand_landmarks in hands_list:
                self.mp_drawing.draw_landmarks(
                    frame_bgr,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )

                # — WAVE DETECTION (unchanged) —
                wrist_x = hand_landmarks.landmark[0].x
                if self.prev_hand_x is not None:
                    if abs(wrist_x - self.prev_hand_x) > 0.05:
                        self.wave_counter += 1
                        if self.wave_counter > 5:
                            self.is_waving = not self.is_waving
                            self.wave_counter = 0
                self.prev_hand_x = wrist_x

                # — THUMBS‐UP DETECTION —
                current_thumb = self._is_thumbs_up(hand_landmarks)
                if current_thumb and not self.prev_thumbs_up and not self.is_clapping:
                    self.is_thumbs_up = True
                self.prev_thumbs_up = current_thumb

                # — PEACE‐SIGN DETECTION —
                current_peace = self._is_peace_sign(hand_landmarks)
                if current_peace and not self.prev_peace_sign and not self.is_clapping:
                    self.is_peace_sign = True
                self.prev_peace_sign = current_peace

        else:
            # No hands detected: reset prev_hand_x so wave restarts cleanly
            self.prev_hand_x = None
            # Also reset previous gesture states so the next appearance can re‐trigger
            self.prev_thumbs_up = False
            self.prev_peace_sign = False
            # Note: for clap, we let prev_clapping remain until two‐hand detection reoccurs

        return frame_bgr, pose_results, {
            'is_waving': self.is_waving,
            'is_thumbs_up': self.is_thumbs_up,
            'is_peace_sign': self.is_peace_sign,
            'is_clapping': self.is_clapping
        }

    def get_landmarks(self, results):
        """Extract coordinates for specific pose landmarks (right_wrist, left_wrist, head)."""
        if not results.pose_landmarks:
            return {}
        landmarks = {
            'right_wrist': results.pose_landmarks.landmark[
                self.mp_pose.PoseLandmark.RIGHT_WRIST
            ],
            'left_wrist':  results.pose_landmarks.landmark[
                self.mp_pose.PoseLandmark.LEFT_WRIST
            ],
            'head':        results.pose_landmarks.landmark[
                self.mp_pose.PoseLandmark.NOSE
            ]
        }
        return landmarks

    # —————— Gesture Helper Methods ——————

    def _is_thumbs_up(self, hand_landmarks) -> bool:
        """Return True if only the thumb is extended, all other fingers folded."""
        lm = hand_landmarks.landmark
        # Thumb extended if tip is above IP in y
        thumb_ext = lm[4].y < lm[3].y
        # Other fingers folded if tip is below PIP
        index_fold = lm[8].y > lm[6].y
        middle_fold = lm[12].y > lm[10].y
        ring_fold = lm[16].y > lm[14].y
        pinky_fold = lm[20].y > lm[18].y
        return thumb_ext and index_fold and middle_fold and ring_fold and pinky_fold

    def _is_peace_sign(self, hand_landmarks) -> bool:
        """Return True if index & middle are extended, ring/pinky/thumb folded."""
        lm = hand_landmarks.landmark
        index_ext = lm[8].y < lm[6].y
        middle_ext = lm[12].y < lm[10].y
        ring_fold = lm[16].y > lm[14].y
        pinky_fold = lm[20].y > lm[18].y
        thumb_fold = lm[4].y > lm[3].y

        # Check distance between index & middle tips so they form a V (not too far apart)
        dist_im = ((lm[8].x - lm[12].x)**2 + (lm[8].y - lm[12].y)**2)**0.5
        # Only a peace sign if V is reasonably close (tweak 0.1 if needed)
        return index_ext and middle_ext and ring_fold and pinky_fold and thumb_fold and (dist_im < 0.1)

    def _is_clapping(self, hands_list) -> bool:
        """Return True if two hands’ wrists are very close in 3D space."""
        lm1 = hands_list[0].landmark
        lm2 = hands_list[1].landmark
        x1, y1, z1 = lm1[0].x, lm1[0].y, lm1[0].z
        x2, y2, z2 = lm2[0].x, lm2[0].y, lm2[0].z
        dist = ((x1 - x2)**2 + (y1 - y2)**2 + (z1 - z2)**2) ** 0.5
        return dist < 0.08  # Adjust threshold after testing
