import os
import sys
import time

import cv2
import mediapipe as mp

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    __package__ = "hand_control"

from . import state
from .camera import create_detector, open_camera
from .config import MODES, WIN
from .hand_utils import draw_hand, fingers_up, hand_size
from .media_controls import BrightnessWorker, init_volume, sbc
from .mode_selection import set_mode, update_selection
from .modes import HANDLERS
from .state import S
from .ui import draw_ui


def main():
    cap = open_camera()
    if not cap.isOpened():
        print("Khong mo duoc camera.")
        return

    detector = create_detector()
    init_volume()
    if sbc is not None:
        state.brightness_worker = BrightnessWorker()
        state.brightness_worker.start()

    cv2.namedWindow(WIN)
    cv2.moveWindow(WIN, 50, 50)

    start_time = time.time()
    last_ts = -1
    prev_time = time.time()
    fps = 0.0

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        timestamp = int((time.time() - start_time) * 1000)
        if timestamp <= last_ts:
            timestamp = last_ts + 1
        last_ts = timestamp
        result = detector.detect_for_video(mp_img, timestamp)

        now = time.time()
        if result.hand_landmarks:
            landmarks = [(point.x, point.y) for point in result.hand_landmarks[0]]
            draw_hand(frame, landmarks)
            fingers = fingers_up(landmarks)
            if not update_selection(fingers, now):
                HANDLERS[S["mode"]](landmarks, fingers, hand_size(landmarks), now)
        else:
            S["status"] = "No hand"
            S["fist_start"] = None
            S["v_start"] = None
            S["pinch_l"] = S["pinch_r"] = False

        fps = 0.9 * fps + 0.1 * (1 / max(now - prev_time, 1e-6))
        prev_time = now
        draw_ui(frame, fps)
        cv2.imshow(WIN, frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if key in (ord("1"), ord("2"), ord("3"), ord("4")):
            set_mode(MODES[int(chr(key))], time.time())

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
