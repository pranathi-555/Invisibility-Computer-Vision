import cv2
import numpy as np
import time

from engine import (
    BackgroundModel,
    SegmentationEngine,
    HandTracker,
    PortalBox,
    HUD
)

WINDOW = "Cinematic Cloak"


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

    seg = SegmentationEngine()
    tracker = HandTracker()
    bg = BackgroundModel(h, w)
    portal = PortalBox()
    hud = HUD()

    print("Stand still for background capture...")

    # =========================
    # BACKGROUND CALIBRATION
    # =========================
    start = time.time()
    while time.time() - start < 3:
        ret, frame = cap.read()
        if not ret:
            continue

        bg.update(frame.astype(np.float32))

        cv2.imshow(WINDOW, frame)
        if cv2.waitKey(1) & 0xFF == 27:
            cap.release()
            cv2.destroyAllWindows()
            return

    print("Ready!")

    # =========================
    # MAIN LOOP
    # =========================
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = frame.astype(np.uint8)

        mask = seg.get_mask(frame)
        results = tracker.process(frame)
        info = tracker.get_info(results, w, h)

        portal.update(info)
        portal.update_alpha()

        frame = portal.render(frame, mask, bg.get(), info["points"])
        frame = hud.draw(frame, portal, info)

        cv2.imshow(WINDOW, frame)

        key = cv2.waitKey(1) & 0xFF
        if key in (27, ord('q')):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()