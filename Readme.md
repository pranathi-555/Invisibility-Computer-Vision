# Gesture-Controlled Dynamic Invisibility Portal Using Computer Vision and Hand Tracking

An AI-powered Computer Vision project that creates a real-time dynamic invisibility portal using hand gesture recognition. The system detects hand gestures using MediaPipe Hands and OpenCV, allowing users to activate or deactivate an invisibility portal through intuitive pinch gestures.

---

## Project Overview

This project demonstrates the application of Computer Vision, Artificial Intelligence, and Human-Computer Interaction by enabling users to create a dynamic invisibility portal using only hand gestures.

Unlike traditional invisibility cloak projects that require colored cloth, this system uses real-time hand tracking to control an invisible portal. The portal replaces a selected region of the live camera feed with a previously captured background, creating the illusion of invisibility.

---

## Features

- Real-time hand tracking using MediaPipe
- Double-hand pinch gesture detection
- Dynamic invisibility portal creation
- Background calibration
- Real-time portal activation and deactivation
- Smooth portal transition
- Live HUD (Heads-Up Display)
- Beginner-friendly implementation
- Modular and object-oriented Python code

---

## Technologies Used

- Python 3.12+
- OpenCV
- MediaPipe
- NumPy

---

## Project Structure

```
Invisibility-Computer-Vision/
│
├── main.py
├── engine.py
├── requirements.txt
├── README.md
├── LICENSE
├── screenshots/
│   ├── home.png
│   ├── portal.png
│   └── gesture.png
│
└── demo/
    └── demo.mp4
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/pranathi-555/Invisibility-Computer-Vision.git
```

### Navigate

```bash
cd Invisibility-Computer-Vision
```

### Install Requirements

```bash
pip install -r requirements.txt
```

### Run

```bash
python main.py
```

---

## How It Works

### Step 1

The application captures the background for a few seconds while the user stands outside the camera view.

### Step 2

MediaPipe detects both hands and tracks 21 landmarks for each hand.

### Step 3

When both hands perform a pinch gesture, the system activates the invisibility portal.

### Step 4

The portal region is replaced with the captured background, creating the illusion of invisibility.

### Step 5

Perform the gesture again to deactivate the portal.

---

## Workflow


Webcam
   │
   ▼
Capture Background
   │
   ▼
Hand Detection
(MediaPipe)
   │
   ▼
Gesture Recognition
(Double Pinch)
   │
   ▼
Portal Generation
   │
   ▼
Background Replacement
   │
   ▼
Display Output



## Future Improvements

- AI gesture recognition using deep learning
- Gesture customization
- Voice-controlled portal
- Multi-portal support
- AR integration
- Object tracking
- GPU acceleration
- Web application deployment
- Mobile application version

---

## Applications

- Human-Computer Interaction
- Augmented Reality
- Virtual Reality
- AI-based Smart Interfaces
- Entertainment
- Education
- Interactive Exhibitions
- Computer Vision Research

---

## Author

**Pranathi Kurapati**

Electronics and Communication Engineering

GitHub:
https://github.com/pranathi-555



---

## License

This project is developed for educational and research purposes.

MIT License
