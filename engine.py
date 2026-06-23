import cv2
import numpy as np
import collections

# =========================
# BACKGROUND MODEL
# =========================
class BackgroundModel:
    def __init__(self, h, w, n_frames=90):
        self.buf = collections.deque(maxlen=n_frames)
        self.bg = None
        self.ready = False

    def update(self, frame):
        self.buf.append(frame.astype(np.float32))

        if len(self.buf) > 20:
            self.bg = np.mean(self.buf, axis=0).astype(np.float32)
            self.ready = True

    def get(self):
        return self.bg if self.ready else None


# =========================
# SEGMENTATION ENGINE
# =========================
class SegmentationEngine:
    def __init__(self):
        import mediapipe as mp
        self.seg = mp.solutions.selfie_segmentation.SelfieSegmentation(1)
        self.prev = None

    def get_mask(self, frame):
        h, w = frame.shape[:2]

        small = cv2.resize(frame, (320, 180))
        res = self.seg.process(cv2.cvtColor(small, cv2.COLOR_BGR2RGB))

        if res.segmentation_mask is None:
            return np.zeros((h, w), np.float32)

        mask = cv2.resize(res.segmentation_mask, (w, h))

        # smoothing
        if self.prev is not None:
            mask = 0.7 * self.prev + 0.3 * mask

        mask = cv2.GaussianBlur(mask, (21, 21), 0)
        mask = np.clip(mask, 0, 1)

        self.prev = mask
        return mask


# =========================
# HAND TRACKER
# =========================
class HandTracker:
    def __init__(self):
        import mediapipe as mp
        self.hands = mp.solutions.hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.5
        )

    def process(self, frame):
        h, w = frame.shape[:2]
        small = cv2.resize(frame, (640, 360))
        return self.hands.process(cv2.cvtColor(small, cv2.COLOR_BGR2RGB))

    def get_info(self, results, w, h):
        info = {
            "hand_count": 0,
            "pinch": False,
            "points": []   # ✅ FIXED KEY (USED IN MAIN)
        }

        if not results or not results.multi_hand_landmarks:
            return info

        info["hand_count"] = len(results.multi_hand_landmarks)

        for hand in results.multi_hand_landmarks:
            lm = hand.landmark

            thumb = lm[4]
            index = lm[8]

            dist = ((thumb.x - index.x)**2 + (thumb.y - index.y)**2)**0.5

            if dist < 0.05:
                info["pinch"] = True

            info["points"].append([(int(p.x*w), int(p.y*h)) for p in lm])

        return info


# =========================
# PORTAL EFFECT (FIXED + STABLE)
# =========================
class PortalBox:
    def __init__(self):
        self.active = False
        self.alpha = 0.0
        self.cooldown = 0

    def update(self, info):
        if self.cooldown > 0:
            self.cooldown -= 1

        if info["pinch"] and self.cooldown == 0:
            self.active = not self.active
            self.cooldown = 15

    def update_alpha(self):
        target = 1.0 if self.active else 0.0
        self.alpha += (target - self.alpha) * 0.10

    def render(self, frame, mask, bg, points=None):
        if bg is None:
            return frame

        h, w = frame.shape[:2]

        mask3 = mask[:, :, None]

        frame_f = frame.astype(np.float32)
        bg_f = bg.astype(np.float32)

        # =========================
        # CLOAK BLENDING
        # =========================
        blended = frame_f * (1 - mask3 * self.alpha) + bg_f * (mask3 * self.alpha)

        # =========================
        # GLOW FIX (NO AXIS ERROR)
        # =========================
        glow = cv2.GaussianBlur(mask, (31, 31), 0)
        glow = np.clip(glow, 0, 1)

        glow3 = np.dstack([glow, glow, glow])

        tint = np.array([0, 200, 255], dtype=np.float32)
        blended += glow3 * tint * 0.08 * self.alpha

        np.clip(blended, 0, 255, out=blended)
        frame[:] = blended.astype(np.uint8)

        return frame


# =========================
# HUD
# =========================
class HUD:
    def draw(self, frame, portal, info):
        txt = "PINCH TO TOGGLE INVISIBILITY"
        cv2.putText(frame, txt, (20, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)
        return frame