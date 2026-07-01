# Workflow Description

## Overview

This document describes the development workflow for the Duck Hunter game project.

---

## 1. Project Setup

### Prerequisites
- Python 3.10 or higher
- Webcam (for hand gesture detection)
- pip (Python package manager)

### Initial Setup
```bash
# Clone the repository
git clone https://github.com/ameer06/Duck-Hunter--Game.git
cd Duck-Hunter--Game

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Generate game assets (if assets/ is empty)
python generate_assets.py
```

---

## 2. Branch Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Stable, production-ready code |
| `dev` | Active development integration |
| `feature/*` | New features (e.g., `feature/sound-effects`) |
| `fix/*` | Bug fixes (e.g., `fix/camera-detection`) |

### Branching Rules
- Never commit directly to `main`
- Create feature branches from `dev`
- Delete branches after merging

---

## 3. Development Cycle

### Step 1: Create a Branch
```bash
git checkout dev
git pull origin dev
git checkout -b feature/your-feature-name
```

### Step 2: Make Changes
- Edit code in your IDE
- Test changes locally: `python main.py`
- Run hand detection test: `python test_hand.py`

### Step 3: Commit
```bash
git add .
git commit -m "Short description of changes"
```

### Commit Message Convention
```
<type>: <description>

Types:
  feat     - New feature
  fix      - Bug fix
  docs     - Documentation only
  style    - Code style (formatting, no logic change)
  refactor - Code restructuring
  test     - Adding/updating tests
  chore    - Build, CI, or tooling changes
```

### Step 4: Push and Create PR
```bash
git push origin feature/your-feature-name
```
Then create a Pull Request on GitHub targeting `dev`.

### Step 5: Code Review
- Reviewer checks code quality
- Verify game runs without errors
- Merge to `dev` after approval

---

## 4. Testing Workflow

### Before Every Commit
```bash
# Test hand detection works
python test_hand.py

# Full dependency check
python test_hand_detection.py

# Run the game
python main.py
```

### Test Checklist
- [ ] Game launches without errors
- [ ] Webcam feed appears (press W to toggle)
- [ ] Hand gesture detection works (finger gun pose)
- [ ] Ducks spawn and fly across screen
- [ ] Shooting registers hits
- [ ] Score updates correctly
- [ ] Level progression works
- [ ] High scores save and load
- [ ] Pause/resume works (P key)
- [ ] Game over screen displays properly
- [ ] Music mute/unmute works (M key)

---

## 5. Asset Management

### Regenerating Assets
If assets are missing or damaged:
```bash
python generate_assets.py
```

### Asset Structure
```
assets/
├── background.png      # Sky + hills backdrop (1280x720)
├── duck_sheet.png      # 4-frame duck animation (480x100)
├── tree1.png           # Pine tree sprite
├── tree2.png           # Oak tree sprite
├── tree3.png           # Bush tree sprite
├── grass_fg.png        # Foreground grass overlay
├── crosshair.png       # Aiming reticle
├── gunshot.wav         # Shot sound effect
├── bg_music.wav        # Background music loop
└── quack.wav           # Duck quack sound
```

### Adding New Assets
1. Place files in `assets/` directory
2. Use consistent naming: lowercase, underscores
3. PNG for images (transparent backgrounds preferred)
4. WAV for audio (44100Hz, 16-bit)

---

## 6. Release Process

### Version Tagging
```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

### Release Checklist
- [ ] All features tested on multiple webcams
- [ ] README updated with latest features
- [ ] requirements.txt reflects current dependencies
- [ ] No debug prints left in production code
- [ ] Game runs clean for 5+ minutes without crashes

---

## 7. Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| Camera not detected | Press C to cycle camera indices |
| Hand not detected | Improve lighting, keep hand 1-2 feet away |
| Missing assets | Run `python generate_assets.py` |
| Import errors | Run `pip install -r requirements.txt` |
| Low FPS | Close other camera apps, reduce window size |

---

## 8. File Reference

| File | Description |
|------|-------------|
| `main.py` | Entry point, game loop, event handling |
| `game_engine.py` | Duck behavior, scoring, levels, rendering |
| `hand_gesture.py` | MediaPipe hand tracking, gesture detection |
| `highscore.py` | Score persistence (JSON file) |
| `generate_assets.py` | Procedural asset generation with Pillow |
| `test_hand.py` | Quick webcam + hand detection test |
| `test_hand_detection.py` | Full dependency diagnostic |
| `RUN_GAME.bat` | Windows one-click launcher |
