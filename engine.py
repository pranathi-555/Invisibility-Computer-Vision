import cv2
import numpy as np
import collections

# =========================
# BACKGROUND MODEL
# =========================
class BackgroundModel:

    def __init__(self, n_frames=90):
        self.buf = collections.deque(maxlen=n_frames)
        self.bg = None
        self.ready = False

    def update(self, frame):

        self.buf.append(frame.astype(np.float32))

        if len(self.buf) >= self.buf.maxlen:

            self.bg = np.mean(
                np.array(self.buf),
                axis=0
            ).astype(np.float32)

            self.ready = True

    def get(self):
        return self.bg if self.ready else None


# =========================
# HAND TRACKER
# =========================

class HandTracker:

    def __init__(self):
        import mediapipe as mp

        self.mp_hands = mp.solutions.hands

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            model_complexity=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

    # -------------------------
    # Detect Hands
    # -------------------------
    def process(self, frame):

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        return self.hands.process(rgb)

    # -------------------------
    # Extract Information
    # -------------------------
    def get_info(self, results, width, height):

        info = {

            "hand_count": 0,

            "left_pinch": False,
            "right_pinch": False,

            "left_points": None,
            "right_points": None,

            "left_center": None,
            "right_center": None
        }

        if results is None:
            return info

        if results.multi_hand_landmarks is None:
            return info

        info["hand_count"] = len(results.multi_hand_landmarks)

        # Loop through every detected hand
        for hand_landmarks, handedness in zip(
                results.multi_hand_landmarks,
                results.multi_handedness):

            label = handedness.classification[0].label

            landmarks = []

            for lm in hand_landmarks.landmark:

                x = int(lm.x * width)
                y = int(lm.y * height)

                landmarks.append((x, y))

            # -------------------------
            # Pinch Detection
            # -------------------------

            thumb = hand_landmarks.landmark[4]
            index = hand_landmarks.landmark[8]

            distance = np.sqrt(

                (thumb.x - index.x) ** 2 +

                (thumb.y - index.y) ** 2

            )

            pinch = distance < 0.045

            # -------------------------
            # Palm Center
            # -------------------------

            center = landmarks[9]

            # -------------------------
            # Save Left / Right
            # -------------------------

            if label == "Left":

                info["left_points"] = landmarks
                info["left_center"] = center
                info["left_pinch"] = pinch

            else:

                info["right_points"] = landmarks
                info["right_center"] = center
                info["right_pinch"] = pinch

        return info


# =========================
# PORTAL BOX
# =========================

class PortalBox:

    def __init__(self):

        self.active = False
        self.alpha = 0.0

        self.cooldown = 0

        self.rect = None

    # ---------------------------------------
    # Toggle Portal
    # ---------------------------------------

    def update(self, info):

        if self.cooldown > 0:
            self.cooldown -= 1

        if (
            info["left_pinch"]
            and
            info["right_pinch"]
            and
            self.cooldown == 0
        ):

            self.active = not self.active
            self.cooldown = 25

    # ---------------------------------------
    # Smooth Fade
    # ---------------------------------------

    def update_alpha(self):

        target = 1.0 if self.active else 0.0

        speed = 0.12

        self.alpha += (target - self.alpha) * speed

        if abs(target - self.alpha) < 0.01:
            self.alpha = target

    # ---------------------------------------
    # Draw Portal
    # ---------------------------------------

    def render(self, frame, bg, info):

        if bg is None:
            return frame

        if self.alpha <= 0:
            return frame

        if info["hand_count"] < 2:
            return frame

        if (
            info["left_points"] is None
            or
            info["right_points"] is None
        ):
            return frame

        # ---------------------------------------
        # Index Finger Tips
        # ---------------------------------------

        left = info["left_points"][8]
        right = info["right_points"][8]

        x1 = min(left[0], right[0])
        x2 = max(left[0], right[0])

        y1 = min(left[1], right[1])
        y2 = max(left[1], right[1])

        margin = 30

        x1 = max(0, x1 - margin)
        y1 = max(0, y1 - margin)

        x2 = min(frame.shape[1], x2 + margin)
        y2 = min(frame.shape[0], y2 + margin)

        # Save Portal
        self.rect = (x1, y1, x2, y2)

        # ---------------------------------------
        # Replace with Background
        # ---------------------------------------

        frame[y1:y2, x1:x2] = bg[y1:y2, x1:x2].astype(np.uint8)

        # ---------------------------------------
        # Portal Border
        # ---------------------------------------

        color = (255, 255, 0)

        thickness = 3

        cv2.rectangle(

            frame,

            (x1, y1),

            (x2, y2),

            color,

            thickness

        )

        # ---------------------------------------
        # Corner Circles
        # ---------------------------------------

        cv2.circle(frame, (x1, y1), 6, (255,255,255), -1)
        cv2.circle(frame, (x2, y1), 6, (255,255,255), -1)
        cv2.circle(frame, (x1, y2), 6, (255,255,255), -1)
        cv2.circle(frame, (x2, y2), 6, (255,255,255), -1)

        return frame


# =========================
# HUD
# =========================

class HUD:

    def draw(self, frame, portal, info):

        # -------------------------
        # Portal Status
        # -------------------------

        state = "ACTIVE" if portal.active else "OFF"

        color = (0, 255, 0) if portal.active else (0, 0, 255)

        cv2.putText(
            frame,
            f"Portal : {state}",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2
        )

        # -------------------------
        # Hands Detected
        # -------------------------

        cv2.putText(
            frame,
            f"Hands : {info['hand_count']}",
            (20, 65),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2
        )

        # -------------------------
        # Pinch Status
        # -------------------------

        if info["left_pinch"] and info["right_pinch"]:
            pinch = "YES"
            pinch_color = (0, 255, 0)
        else:
            pinch = "NO"
            pinch_color = (0, 0, 255)

        cv2.putText(
            frame,
            f"Double Pinch : {pinch}",
            (20, 95),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            pinch_color,
            2
        )

        # -------------------------
        # Instructions
        # -------------------------

        cv2.putText(
            frame,
            "Use Both Hands",
            (20, frame.shape[0] - 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 255),
            2
        )

        cv2.putText(
            frame,
            "Pinch Both Hands To Toggle Portal",
            (20, frame.shape[0] - 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 255),
            2
        )

        return frame
    

    # =========================
# GLOBAL OBJECTS
# =========================

tracker = HandTracker()
background = BackgroundModel()
portal = PortalBox()
hud = HUD()

background_captured = False


# =========================
# PROCESS FRAME FOR GRADIO
# =========================

def process_frame(frame):

    global background_captured

    if frame is None:
        return None

    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    h, w = frame.shape[:2]

    # Capture background only once
    if not background_captured:
        background.update(frame)

        if background.ready:
            background_captured = True

    # Detect hands
    results = tracker.process(frame)
    info = tracker.get_info(results, w, h)

    # Update portal
    portal.update(info)
    portal.update_alpha()

    # Render portal
    frame = portal.render(
        frame,
        background.get(),
        info
    )

    # Draw HUD
    frame = hud.draw(
        frame,
        portal,
        info
    )

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    return frame