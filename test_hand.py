"""
Quick Hand Detection Test
Run this to verify your webcam and hand detection are working
"""
import cv2
import mediapipe as mp

print("=" * 60)
print("HAND DETECTION TEST")
print("=" * 60)
print("\nTesting webcam and hand detection...")
print("Make a finger gun pose in front of the camera")
print("Press 'q' to quit\n")

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

try:
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    print("✓ MediaPipe initialized")
except Exception as e:
    print(f"✗ MediaPipe failed: {e}")
    input("Press Enter to exit...")
    exit()

# Open webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("✗ Cannot open webcam!")
    input("Press Enter to exit...")
    exit()

print("✓ Webcam opened")
print("\n--- TESTING HAND DETECTION ---")
print("Show your hand to the camera...")

frame_count = 0
hands_detected = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame_count += 1
    
    # Flip for mirror effect
    frame = cv2.flip(frame, 1)
    
    # Convert to RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Detect hands
    results = hands.process(rgb)
    
    # Draw landmarks
    if results.multi_hand_landmarks:
        hands_detected += 1
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        
        # Show success message
        cv2.putText(frame, "HAND DETECTED!", (50, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    else:
        cv2.putText(frame, "NO HAND DETECTED", (50, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    # Show stats
    detection_rate = (hands_detected / frame_count) * 100 if frame_count > 0 else 0
    cv2.putText(frame, f"Detection: {detection_rate:.1f}%", (50, 100), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # Display
    cv2.imshow('Hand Detection Test - Press Q to quit', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

print("\n" + "=" * 60)
print("TEST RESULTS:")
print(f"  Total frames: {frame_count}")
print(f"  Hands detected: {hands_detected}")
print(f"  Detection rate: {detection_rate:.1f}%")
print("=" * 60)

if detection_rate > 50:
    print("\n✓ Hand detection is WORKING!")
    print("  Your game should work fine.")
else:
    print("\n⚠ Low detection rate!")
    print("  Tips:")
    print("  - Improve lighting")
    print("  - Keep hand 1-2 feet from camera")
    print("  - Show your full hand clearly")

input("\nPress Enter to exit...")
