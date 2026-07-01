# Workflow Prompt

Use the following prompt to generate or document the project workflow:

---

## Prompt

```
I am building a Duck Hunter game in Python using Pygame, OpenCV, and MediaPipe for hand gesture controls. The project is hosted on GitHub. Describe a complete development workflow for this project that includes:

1. Project setup instructions (clone, virtual environment, pip install, asset generation)
2. Git branching strategy (main, dev, feature branches) with clear naming conventions
3. Step-by-step development cycle from creating a branch to merging a PR
4. Commit message format using conventional commits (feat, fix, docs, refactor, test, chore)
5. Pre-commit testing checklist: verify hand detection with test_hand.py, run full diagnostics with test_hand_detection.py, and playtest the game with python main.py
6. Asset management: how to regenerate assets with generate_assets.py, file naming rules, supported formats (PNG for images, WAV for audio at 44100Hz)
7. Release process: version tagging with git tag, release checklist before shipping
8. Troubleshooting common issues (camera not detected, hand not tracking, missing assets, import errors, low FPS)
9. File-by-file reference explaining what each file does (main.py, game_engine.py, hand_gesture.py, highscore.py, generate_assets.py)

The workflow should be practical, easy to follow, and suitable for a solo developer or small team.
```

---

## Short Version

```
Describe a Git-based development workflow for a Python Pygame + OpenCV + MediaPipe game project. Include setup, branching, commits, testing, asset management, releases, and troubleshooting.
```
