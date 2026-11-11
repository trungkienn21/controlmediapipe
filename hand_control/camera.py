import os
import sys
import urllib.request

import cv2
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from .config import CAM_H, CAM_W, MODEL_FILE, MODEL_URL


def create_detector():
    if not os.path.exists(MODEL_FILE):
        print("Dang tai model hand_landmarker.task ...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_FILE)
    with open(MODEL_FILE, "rb") as model_file:
        data = model_file.read()
    options = vision.HandLandmarkerOptions(
        base_options=python.BaseOptions(model_asset_buffer=data),
        running_mode=vision.RunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=0.6,
        min_hand_presence_confidence=0.6,
        min_tracking_confidence=0.6,
    )
    return vision.HandLandmarker.create_from_options(options)


def open_camera():
    if sys.platform == "win32":
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    else:
        cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_H)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    return cap
