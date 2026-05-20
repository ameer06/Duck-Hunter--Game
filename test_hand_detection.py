"""
Test script to diagnose hand detection issues
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
        print("✓ Camera works!")
        print(f"  Frame shape: {frame.shape}")
    else:
        print("✗ Camera failed to capture")
    cap.release()
except Exception as e:
    print(f"✗ Camera error: {e}")

# Test 2: Check MediaPipe
print("\n=== TEST 2: MediaPipe ===")
try:
    import mediapipe as mp
    print(f"✓ MediaPipe installed: {mp.__version__}")
    print(f"  Available: {dir(mp)}")
    
    # Check if solutions exists
    if hasattr(mp, 'solutions'):
        print("✓ mp.solutions exists (old API)")
        if hasattr(mp.solutions, 'hands'):
            print("✓ mp.solutions.hands exists")
    else:
        print("✗ mp.solutions NOT found (new API)")
        
    if hasattr(mp, 'tasks'):
        print("✓ mp.tasks exists (new API)")
except Exception as e:
    print(f"✗ MediaPipe error: {e}")

# Test 3: Check cvzone
print("\n=== TEST 3: cvzone ===")
try:
    import cvzone
    print(f"✓ cvzone installed: {cvzone.__version__}")
    
    from cvzone.HandTrackingModule import HandDetector
    detector = HandDetector(detectionCon=0.5, maxHands=1)
    print("✓ HandDetector created successfully")
    
    # Quick test with camera
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if ret:
        try:
            hands, img = detector.findHands(frame, draw=True)
            print(f"✓ Hand detection ran - found {len(hands) if hands else 0} hands")
        except Exception as e:
            print(f"✗ Hand detection error: {e}")
    cap.release()
    
except ImportError as e:
    print(f"✗ cvzone not installed: {e}")
except Exception as e:
    print(f"✗ cvzone error: {e}")

# Test 4: OpenCV
print("\n=== TEST 4: OpenCV ===")
try:
    import cv2
    print(f"✓ OpenCV installed: {cv2.__version__}")
except Exception as e:
    print(f"✗ OpenCV error: {e}")

print("\n=== SUMMARY ===")
print("If all tests pass, hand detection should work.")
print("If cvzone test fails, we'll use direct MediaPipe instead.")
