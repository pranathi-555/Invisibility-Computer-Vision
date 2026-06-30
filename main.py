import cv2
import time

from engine import (
    BackgroundModel,
    HandTracker,
    PortalBox,
    HUD
)

WINDOW = "Gesture Controlled Dynamic Invisibility Portal"


def main():

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Camera not found")
        return

    ret, frame = cap.read()

    if not ret:
        print("Failed to read camera")
        return

    h, w = frame.shape[:2]

    tracker = HandTracker()
    bg = BackgroundModel()
    portal = PortalBox()
    hud = HUD()

    print("Stand still for background capture...")

    # --------------------------
    # Background Capture
    # --------------------------

    start = time.time()

    while time.time() - start < 5:

        ret, frame = cap.read()

        if not ret:
            continue

        bg.update(frame)

        cv2.putText(
            frame,
            "Capturing Background...",
            (20,40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0,255,255),
            2
        )

        cv2.imshow(WINDOW, frame)

        if cv2.waitKey(1) & 0xFF == 27:
            cap.release()
            cv2.destroyAllWindows()
            return

    print("Ready!")

    # --------------------------
    # Main Loop
    # --------------------------

    while True:

        ret, frame = cap.read()

        if not ret:
            continue

        results = tracker.process(frame)

        info = tracker.get_info(results, w, h)

        portal.update(info)

        portal.update_alpha()

        frame = portal.render(
            frame,
            bg.get(),
            info
        )

        frame = hud.draw(
            frame,
            portal,
            info
        )

        cv2.imshow(WINDOW, frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("b"):
           bg.capture(frame)
           print("Background Captured!")

        if key == 27 or key == ord("q"):
            break

    cap.release()

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()