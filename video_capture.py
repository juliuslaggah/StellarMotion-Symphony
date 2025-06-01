import cv2

class VideoCapture:
    def __init__(self, width=640, height=480):
        """Initialize the webcam with specified resolution."""
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        if not self.cap.isOpened():
            raise RuntimeError("Error: Could not open webcam.")
    
    def get_frame(self):
        """Capture and return a single frame."""
        ret, frame = self.cap.read()
        if not ret:
            return None
        # Resize for consistency
        frame = cv2.resize(frame, (640, 480))
        return frame
    
    def release(self):
        """Release the webcam and clean up."""
        self.cap.release()
        
        
        