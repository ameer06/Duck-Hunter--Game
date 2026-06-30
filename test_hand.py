"""
Quick Hand Detection Test
Run this to verify your webcam and hand detection are working.
Press 'q' to quit.
"""
import cv2
import mediapipe as mp


def main():
    print("=" * 60)
    print("HAND DETECTION TEST")
    print("=" * 60)
    print("\nTesting webcam and hand detection...")
    print("Make a finger gun pose in front of the camera")
    print("Press 'q' to quit\n")

    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils

    try:
        hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        print("MediaPipe initialized")
    except Exception as e:
        print(f"MediaPipe failed: {e}")
        return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open webcam!")
        return

    print("Webcam opened")
    print("\n--- TESTING HAND DETECTION ---")
    print("Show your hand to the camera...\n")

    frame_count = 0
    hands_detected = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            if results.multi_hand_landmarks:
                hands_detected += 1
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                cv2.putText(frame, "HAND DETECTED!", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "NO HAND DETECTED", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            detection_rate = (hands_detected / frame_count) * 100
            cv2.putText(frame, f"Detection: {detection_rate:.1f}%", (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            cv2.imshow("Hand Detection Test - Press Q to quit", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
        hands.close()

    print("\n" + "=" * 60)
    print("TEST RESULTS:")
    print(f"  Total frames: {frame_count}")
    print(f"  Hands detected: {hands_detected}")
    print(f"  Detection rate: {detection_rate:.1f}%")
    print("=" * 60)

    if detection_rate > 50:
        print("\nHand detection is WORKING! Your game should work fine.")
    else:
        print("\nLow detection rate! Tips:")
        print("  - Improve lighting")
        print("  - Keep hand 1-2 feet from camera")
        print("  - Show your full hand clearly")


if __name__ == "__main__":
    main()
