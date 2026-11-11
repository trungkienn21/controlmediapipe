import numpy as np
import pyautogui

from ..config import CLICK_COOLDOWN, MARGIN, PINCH_RATIO, SCROLL_AMOUNT, SMOOTH
from ..hand_utils import dist
from ..state import S, screen_h, screen_w


def move_cursor(landmarks):
    x = np.interp(landmarks[8][0], (MARGIN, 1 - MARGIN), (0, screen_w - 1))
    y = np.interp(landmarks[8][1], (MARGIN, 1 - MARGIN), (0, screen_h - 1))
    S["prev_x"] += (x - S["prev_x"]) / SMOOTH
    S["prev_y"] += (y - S["prev_y"]) / SMOOTH
    pyautogui.moveTo(S["prev_x"], S["prev_y"])


def mode_mouse(landmarks, fingers, size, now):
    _, index, middle, ring, pinky = fingers
    pinch_left = (
        dist(landmarks[4], landmarks[12]) / size < PINCH_RATIO
        and dist(landmarks[0], landmarks[12]) / size > 1.15
    )
    pinch_right = dist(landmarks[8], landmarks[20]) / size < PINCH_RATIO

    if pinch_right:
        S["status"] = "Right click"
        if not S["pinch_r"] and now - S["last_click"] > CLICK_COOLDOWN:
            pyautogui.click(button="right")
            S["last_click"] = now
        S["pinch_r"], S["pinch_l"] = True, False
        return
    S["pinch_r"] = False

    if pinch_left:
        S["status"] = "Left click"
        if not S["pinch_l"] and now - S["last_click"] > CLICK_COOLDOWN:
            pyautogui.click()
            S["last_click"] = now
        S["pinch_l"] = True
        return
    S["pinch_l"] = False

    if index and not (middle or ring or pinky):
        S["status"] = "Move"
        move_cursor(landmarks)
    elif middle and not (index or ring or pinky):
        S["status"] = "Scroll UP"
        pyautogui.scroll(SCROLL_AMOUNT)
    elif pinky and not (index or middle or ring):
        S["status"] = "Scroll DOWN"
        pyautogui.scroll(-SCROLL_AMOUNT)
    else:
        S["status"] = "Idle"
