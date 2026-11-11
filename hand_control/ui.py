import time

import cv2
import numpy as np

from .config import MARGIN
from .media_controls import sbc
from .state import S


def draw_bar(frame, x, value, label, color):
    height = frame.shape[0]
    top, bottom = 90, height - 40
    cv2.rectangle(frame, (x, top), (x + 25, bottom), (255, 255, 255), 2)
    fill = int(np.interp(value, (0, 100), (bottom, top)))
    cv2.rectangle(frame, (x, fill), (x + 25, bottom), color, -1)
    cv2.putText(frame, label, (x - 5, bottom + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)


def draw_ui(frame, fps):
    height, width, _ = frame.shape
    x1, y1 = int(width * MARGIN), int(height * MARGIN)
    x2, y2 = int(width * (1 - MARGIN)), int(height * (1 - MARGIN))
    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 2)

    cv2.putText(frame, f"MODE: {S['mode']}", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    cv2.putText(frame, S["status"], (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.putText(frame, f"FPS: {int(fps)}", (width - 100, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
    if time.time() - S["msg_time"] < 2:
        cv2.putText(frame, S["msg"], (10, height - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)

    if S["mode"] == "VOLUME":
        draw_bar(frame, width - 45, S["vol"], "VOL", (0, 255, 0))
    elif S["mode"] == "BRIGHTNESS":
        draw_bar(frame, width - 45, S["bright"], "BRI", (0, 220, 255))
        if sbc is None:
            cv2.putText(
                frame, "Chua cai screen-brightness-control", (10, 85),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1,
            )
