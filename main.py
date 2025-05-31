import cv2
from video_capture import VideoCapture
from pose_estimation import PoseEstimation
from osc_communication import OSCCommunication

def main():
    video = VideoCapture()
    pose = PoseEstimation()
    osc = OSCCommunication()
    
    try:
        while True:
            frame = video.get_frame()
            if frame is None:
                print("Error: Could not read frame.")
                break
            
            # Process frame for pose and hands
            annotated_frame, pose_results, gesture_data = pose.process_frame(frame)
            
            # Extract and send pose landmarks
            landmarks = pose.get_landmarks(pose_results)
            if landmarks:
                osc.send_landmarks(landmarks)
            
            # Send gesture data
            osc.client.send_message("/gesture/waving", [int(gesture_data['is_waving'])])
            
            cv2.imshow('Pose Estimation', annotated_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    finally:
        video.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()