# Duck Hunter - Hand Gesture Game

A gesture-controlled duck hunting game inspired by the classic Duck Hunt. Uses your webcam to track hand movements!

## About
This project uses computer vision to detect hand gestures and lets you shoot ducks by making a finger gun pose. Built with Python, OpenCV, and MediaPipe.

## How It Works
- Camera tracks your hand in real-time
- Make a finger gun pose (index finger out, thumb up)
- Aim at the ducks with your finger
- Pull the trigger by moving your thumb down and back up
- Score points by hitting ducks!

## Requirements
```
opencv-python
mediapipe
pygame-ce
numpy
```

Install with: `pip install -r requirements.txt`

## Running the Game

**Easy way:**
- Just double-click `RUN_GAME.bat`

**Or from terminal:**
```
python main.py
```

## Controls
- **Hand Gesture**: Make finger gun pose to aim
- **Thumb Motion**: Quick down-up motion to shoot
- **W Key**: Toggle webcam preview
- **F Key**: Show/hide FPS
- **ESC**: Quit game

## Tips
- Make sure you have good lighting
- Keep your hand 1-2 feet from the camera  
- Hold the finger gun pose steady to see the crosshair
- Watch for the green circles around ducks - that's the hit zone!

## Game Features
- Hand tracking using MediaPipe
- Score tracking and accuracy stats
- Combo multipliers for consecutive hits
- Visual effects (muzzle flash, recoil)
- Hit detection radius of 180px (pretty forgiving!)

## Project Structure
```
duck hunter/
├── main.py              # Main game loop
├── hand_gesture.py      # Hand detection logic
├── game_engine.py       # Duck behavior and scoring
├── generate_assets.py   # Creates fallback game assets
├── requirements.txt     # Dependencies
└── assets/              # Game sprites (duck, background, crosshair)
```

## Troubleshooting

**Crosshair not appearing:**
- Check if webcam is working (press W to see preview)
- Make sure proper finger gun pose (index out, thumb up, others folded)
- Improve lighting conditions

**Shooting not working:**
- Make sure you're holding the finger gun pose
- Try making a more obvious thumb motion (down then up quickly)
- Check the green "READY ✓" indicator appears

**Low frame rate:**
- Close other camera applications
- Reduce game window if needed

## Credits
Made by: Mohamed
Inspired by: Classic Nintendo Duck Hunt
