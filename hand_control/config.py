import os


CAM_W, CAM_H = 640, 480
MARGIN = 0.15
SMOOTH = 4
PINCH_RATIO = 0.30
CLICK_COOLDOWN = 0.5
SCROLL_AMOUNT = 40
VOL_RANGE = (0.2, 1.2)
FIST_HOLD = 0.8
SELECT_HOLD = 0.6
SELECT_TIMEOUT = 6.0
V_HOLD = 0.4
SHOT_COOLDOWN = 2.0

MODEL_FILE = "hand_landmarker.task"
MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
)
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAVE_DIR = os.path.join(PROJECT_DIR, "screenshots")
WIN = "Hand Control"

MODES = {1: "MOUSE", 2: "VOLUME", 3: "BRIGHTNESS", 4: "SCREENSHOT"}

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12), (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20), (0, 17),
]
