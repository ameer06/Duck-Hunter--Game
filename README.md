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
pygame
numpy
```

Install with: `pip install -r requirements.txt`

## Running the Game

**Desktop version (original):**

Easy way:
- Just double-click `RUN_GAME.bat`

Or from terminal:
```
python main.py
```

**Web version (Flask):**
```
pip install flask
python app.py
```
Then open `http://localhost:5000` in your browser. Works with webcam or mouse!

**Deploy web version online:**
```
# Render.com (free)
# 1. Push to GitHub
# 2. Connect repo on render.com
# 3. Build: pip install -r requirements.txt
# 4. Start: gunicorn app:app

# Railway.app
# 1. Push to GitHub
# 2. Connect repo on railway.app
# 3. Auto-detects Python and Procfile
```

## Controls
- **Hand Gesture**: Make finger gun pose to aim
- **Thumb Motion**: Quick down-up motion to shoot
- **Mouse**: Aim with cursor, left-click to shoot (when no camera)
- **SPACE**: Start game from menu
- **P Key**: Pause / Resume
- **W Key**: Toggle webcam preview
- **M Key**: Mute / Unmute background music
- **C Key**: Cycle camera (if webcam not working)
- **F Key**: Show/hide FPS
- **H Key**: Toggle hitbox debug view
- **R Key**: Restart (on game over screen)
- **Y/N Key**: Confirm/Cancel quit from menu
- **UP/DOWN Arrows**: Adjust music volume
- **ESC**: Quit game

## Tips
- Make sure you have good lighting
- Keep your hand 1-2 feet from the camera  
- Hold the finger gun pose steady to see the crosshair
- Watch for the green circles around ducks - that's the hit zone!
- No camera? The game auto-detects and switches to mouse mode

## Game Features
- Hand tracking using MediaPipe
- Mouse fallback mode when no camera is available
- Main menu screen with controls guide, leaderboard, and game count
- Score tracking and accuracy stats
- High score persistence (top 5 scores saved with timestamps)
- Session best tracker across multiple games
- Difficulty progression with leveling system and level progress display
- Combo multipliers for consecutive hits with highest combo tracking
- Visual effects (muzzle flash, recoil, feather particles with fade-out)
- Screen shake on shot (stronger on hit, lighter on miss)
- Streak announcements (Double Kill, Triple Kill, etc.)
- Ammo warning flash when low
- Ducks escaped counter and active ducks display in HUD
- Pause/resume with live stats display
- Hitbox debug view (H key)
- Music volume controls (UP/DOWN arrows)
- Quit confirmation prompt on menu
- CLI flags: `--help`, `--no-camera`
- Hit detection targets closest duck to aim point
- Hit detection radius of 180px (pretty forgiving!)

## Project Structure
```
duck hunter/
├── main.py                  # Main game loop (desktop)
├── app.py                   # Flask web server
├── templates/
│   └── index.html           # Browser game (Canvas + MediaPipe JS)
├── hand_gesture.py          # Hand detection logic
├── game_engine.py           # Duck behavior, scoring, and levels
├── highscore.py             # High score persistence (desktop)
├── generate_assets.py       # Creates fallback game assets
├── requirements.txt         # Dependencies
├── RUN_GAME.bat             # One-click launcher (Windows)
├── assets/                  # Game sprites and sounds
│   ├── background.png       # Sky and hills backdrop
│   ├── duck_sheet.png       # 4-frame duck animation
│   ├── tree1/2/3.png        # Tree sprites at various depths
│   ├── grass_fg.png         # Foreground grass overlay
│   ├── crosshair.png        # Aiming reticle
│   ├── gunshot.wav          # Shot sound effect
│   ├── bg_music.wav         # Background music loop
│   └── quack.wav            # Duck quack sound
├── test_hand.py             # Quick webcam + hand detection test
└── test_hand_detection.py   # Full dependency diagnostic tool
```

## Troubleshooting

**No camera detected:**
- The game will automatically switch to mouse mode
- Use your mouse to aim and left-click to shoot
- Press C to cycle through camera indices if needed

**Crosshair not appearing:**
- Check if webcam is working (press W to see preview)
- Make sure proper finger gun pose (index out, thumb up, others folded)
- In mouse mode, the crosshair follows your cursor automatically

**Shooting not working:**
- Make sure you're holding the finger gun pose
- Try making a more obvious thumb motion (down then up quickly)
- Check the green "READY ✓" indicator appears
- In mouse mode, use left-click to shoot

**Low frame rate:**
- Close other camera applications
- Reduce game window if needed

## Credits
Made by: Mohamed
Inspired by: Classic Nintendo Duck Hunt
