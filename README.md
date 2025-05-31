StellarMotion Symphony
Overview
This project creates an interactive art installation where a user’s body movements, captured via a webcam, drive visual and audio effects in real-time. Using Mediapipe for pose and hand tracking, the Python backend processes the webcam feed and sends landmark data to a Processing sketch via OSC (Open Sound Control). The Processing sketch renders swirling star-shaped particles that follow the user’s movements, with colors changing when a waving gesture is detected. A chime sound plays each time a wave is detected, enhancing the interactive experience.
Features

Pose Tracking: Tracks the user’s right wrist, left wrist, and head using Mediapipe.
Gesture Recognition: Detects a waving gesture to toggle particle colors.
Visual Effects: Renders star-shaped particles in Processing, with sizes scaling based on movement speed.
Audio Effects: Plays a chime sound when a waving gesture is detected, using Processing’s Minim library.
Movement Accuracy: Particles only spawn for landmarks that are actively moving.

Prerequisites

Python 3.8+: For the backend.
Processing 4.x: For the visual and audio effects.
Webcam: To capture user movements.
Sound File: A chime.wav file for the audio effect (place in data/ folder).

Directory Structure
StellarMotion-Symphony/
├── data/
│   └── chime.wav          # Sound file for waving gesture
├── main.py               # Main script to run the backend
├── osc_communication.py  # OSC communication with Processing
├── pose_estimation.py    # Pose and gesture detection
├── video_capture.py      # Webcam capture
├── PoseVisuals.pde       # Processing sketch for visuals and audio
├── requirements.txt      # Python dependencies
└── README.md             # This file

Setup Instructions
1. Clone the Repository
Clone the project from GitHub:
git clone https://github.com/your-username/StellarMotion-Symphony.git
cd StellarMotion-Symphony

2. Python Backend Setup

Set Up a Virtual Environment (optional but recommended):
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install Python Dependencies:
pip install -r requirements.txt

This installs:

opencv-python: For webcam capture and frame processing.
mediapipe: For pose and hand tracking.
python-osc: For OSC communication with Processing.



3. Processing Sketch Setup

Install Processing:

Download and install Processing from processing.org.


Install the Minim Library:

Open Processing, go to Sketch > Import Library > Add Library.
Search for “Minim” and install it.


Add the Sound File:

Place chime.wav in the StellarMotion-Symphony/data/ folder.
If you don’t have a sound file, download a free chime sound from Freesound.org (e.g., search for “chime” and download a .wav file).


Open the Sketch:

Open PoseVisuals.pde in the Processing IDE.



Usage

Run the Processing Sketch:

Open PoseVisuals.pde in Processing.
Click the “Run” button (play icon).


Run the Python Backend:

In a terminal, navigate to the project directory:cd StellarMotion-Symphony


If using a virtual environment, activate it:source venv/bin/activate  # On Windows: venv\Scripts\activate


Run the main script:python main.py




Interact with the Installation:

Stand in front of the webcam.
Move your hands or head to generate star-shaped particles:
Right wrist: Red (or yellow when waving).
Left wrist: Green (or cyan when waving).
Head: Blue (or magenta when waving).


Wave your hand to toggle particle colors and play a chime sound.


Exit:

Press q in the OpenCV window to quit the Python script.
Stop the Processing sketch by closing the window or clicking the stop button.



Troubleshooting

Webcam Not Working:
Ensure your webcam is connected and accessible.
Check video_capture.py for the correct camera index (default is 0).


No Sound:
Verify that chime.wav is in the data/ folder.
Ensure the Minim library is installed in Processing.


Particles Not Spawning:
Adjust movementThreshold in PoseVisuals.pde (e.g., reduce from 5 to 3 if too strict).


Mediapipe Errors:
Ensure mediapipe is installed correctly (pip install mediapipe).
Check your webcam feed quality and lighting conditions.



Future Enhancements

Multi-Person Support: Explore using a library like OpenPose for reliable multi-person tracking.
More Visual Effects: Add different particle shapes or patterns.
Additional Sounds: Play different sounds for each landmark’s movement.

Authors

Julius (and team)
With assistance from Grok (xAI)

License
This project is for educational purposes and internal team use. Please do not distribute without permission.

Last Updated: May 31, 2025
