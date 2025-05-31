from pythonosc import udp_client

class OSCCommunication:
    def __init__(self, ip="127.0.0.1", port=12000):
        """Initialize OSC client."""
        self.client = udp_client.SimpleUDPClient(ip, port)
    
    def send_landmarks(self, landmarks):
        """Send landmark coordinates via OSC."""
        for name, landmark in landmarks.items():
            self.client.send_message(f"/pose/{name}", [float(landmark.x), float(landmark.y), float(landmark.z)])