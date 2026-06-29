"""
Test script to diagnose hand detection issues
Uses only OpenCV and MediaPipe (no cvzone dependency)
"""
import cv2
import sys

print(f"Python version: {sys.version}")

# Test 1: Check if camera works
print("\n=== TEST 1: Camera ===")
try:
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if ret:
        print("Camera works!")
        print(f"  Frame shape: {frame.shape}")
    else:
        print("Camera failed to capture")
    cap.release()
except Exception as e:
    print(f"Camera error: {e}")

# Test 2: Check MediaPipe
print("\n=== TEST 2: MediaPipe ===")
try:
    import mediapipe as mp
    print(f"MediaPipe installed: {mp.__version__}")

    if hasattr(mp, 'solutions'):
        print("  mp.solutions exists (legacy API)")
        if hasattr(mp.solutions, 'hands'):
            print("  mp.solutions.hands exists")
    else:
        print("  mp.solutions NOT found (new API only)")

    if hasattr(mp, 'tasks'):
        print("  mp.tasks exists (new API)")

    # Test hands detection with solutions API
    if hasattr(mp, 'solutions') and hasattr(mp.solutions, 'hands'):
        print("\n  Testing hands detection...")
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if ret:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)
            if results.multi_hand_landmarks:
                print(f"  Hand detection working - found {len(results.multi_hand_landmarks)} hand(s)")
            else:
                print("  Hand detection ran but no hand found in test frame")
        cap.release()
        hands.close()
    else:
        print("  Cannot test hands - solutions API not available")

except ImportError as e:
    print(f"MediaPipe not installed: {e}")
except Exception as e:
    print(f"MediaPipe error: {e}")

# Test 3: OpenCV
print("\n=== TEST 3: OpenCV ===")
try:
    print(f"OpenCV installed: {cv2.__version__}")
except Exception as e:
    print(f"OpenCV error: {e}")

# Test 4: Pygame
print("\n=== TEST 4: Pygame ===")
try:
    import pygame
    print(f"Pygame installed: {pygame.__version__}")
except Exception as e:
    print(f"Pygame not installed: {e}")

# Test 5: NumPy
print("\n=== TEST 5: NumPy ===")
try:
    import numpy as np
    print(f"NumPy installed: {np.__version__}")
except Exception as e:
    print(f"NumPy not installed: {e}")

print("\n=== SUMMARY ===")
print("All tests should pass for the game to work correctly.")
print("If MediaPipe hands test fails, hand gesture detection will not work.")
print("Make sure you have good lighting and show your hand clearly to the camera.")
