import time

import cv2
import numpy as np

from .config import HAND_CONNECTIONS
from .state import S


def dist(a, b):
    return np.hypot(a[0] - b[0], a[1] - b[1])


def hand_size(lm):
    return dist(lm[0], lm[9]) + 1e-6


def fingers_up(lm):
    """[thumb, index, middle, ring, pinky] -> 1 = duoi, 0 = gap."""
    fingers = [1 if dist(lm[4], lm[5]) > dist(lm[3], lm[5]) * 1.1 else 0]
    for tip, pip in zip((8, 12, 16, 20), (6, 10, 14, 18)):
        fingers.append(1 if lm[tip][1] < lm[pip][1] else 0)
    return fingers


def draw_hand(frame, lm):
    height, width, _ = frame.shape
    points = [(int(x * width), int(y * height)) for x, y in lm]
    for start, end in HAND_CONNECTIONS:
        cv2.line(frame, points[start], points[end], (255, 255, 255), 2)
    for point in points:
        cv2.circle(frame, point, 4, (0, 255, 0), -1)


def show_msg(text):
    S["msg"], S["msg_time"] = text, time.time()
