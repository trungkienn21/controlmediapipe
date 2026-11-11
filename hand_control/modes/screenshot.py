import os
import time

import cv2
import pyautogui

from ..config import SHOT_COOLDOWN, SAVE_DIR, V_HOLD, WIN
from ..hand_utils import show_msg
from ..state import S


def take_screenshot():
    os.makedirs(SAVE_DIR, exist_ok=True)
    path = os.path.join(SAVE_DIR, time.strftime("screenshot_%Y%m%d_%H%M%S.png"))
    cv2.moveWindow(WIN, -3000, 0)
    cv2.waitKey(250)
    pyautogui.screenshot().save(path)
    cv2.moveWindow(WIN, 50, 50)
    return path


def mode_screenshot(landmarks, fingers, size, now):
    _, index, middle, ring, pinky = fingers
    is_v = index and middle and not (ring or pinky)
    if not is_v:
        S["v_start"] = None
        S["status"] = "Screenshot: giu chu V"
        return
    if S["v_start"] is None:
        S["v_start"] = now
    S["status"] = "Giu chu V..."
    if now - S["v_start"] >= V_HOLD and now - S["last_shot"] > SHOT_COOLDOWN:
        path = take_screenshot()
        S["last_shot"] = time.time()
        S["v_start"] = None
        show_msg("Saved: " + os.path.basename(path))
        print("Da luu:", path)
