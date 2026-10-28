import os
import sys
import time
import threading
import urllib.request

import cv2
import numpy as np
import pyautogui
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

try:
    import screen_brightness_control as sbc
except ImportError:
    sbc = None

# ----------------------------- CAU HINH -----------------------------
CAM_W, CAM_H = 640, 480
MARGIN = 0.15            # vien dem cua vung dieu khien (ti le khung hinh)
SMOOTH = 4               # cang lon con tro cang muot nhung cang tre
PINCH_RATIO = 0.30       # nguong "cham ngon" (chia theo kich thuoc ban tay)
CLICK_COOLDOWN = 0.5
SCROLL_AMOUNT = 40       # luong cuon moi khung hinh
VOL_RANGE = (0.2, 1.2)   # khoang cach ngon cai-tro (da chuan hoa) ung voi 0% -> 100%
FIST_HOLD = 0.8          # giu nam tay de vao chon che do
SELECT_HOLD = 0.6        # giu so ngon de xac nhan che do
SELECT_TIMEOUT = 6.0     # qua thoi gian nay thi huy chon
V_HOLD = 0.4             # giu chu V de chup man hinh
SHOT_COOLDOWN = 2.0

MODEL_FILE = "hand_landmarker.task"
MODEL_URL = ("https://storage.googleapis.com/mediapipe-models/"
             "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task")
SAVE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
WIN = "Hand Control"

MODES = {1: "MOUSE", 2: "VOLUME", 3: "BRIGHTNESS", 4: "SCREENSHOT"}

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12), (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20), (0, 17),
]

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0
screen_w, screen_h = pyautogui.size()

# ----------------------------- TRANG THAI CHUNG -----------------------------
S = {
    "mode": "MOUSE", "status": "", "msg": "", "msg_time": 0.0,
    # chon che do
    "selecting": False, "fist_start": None, "sel_start": 0.0,
    "sel_count": None, "sel_hold": 0.0, "last_mode_change": 0.0,
    # chuot
    "prev_x": pyautogui.position()[0], "prev_y": pyautogui.position()[1],
    "pinch_l": False, "pinch_r": False, "last_click": 0.0,
    # am luong / do sang / chup man hinh
    "vol": 50.0, "vol_applied": 50.0, "bright": 50.0,
    "v_start": None, "last_shot": 0.0,
}

volume_ctl = None
brightness_worker = None


# ----------------------------- TIEN ICH -----------------------------
def dist(a, b):
    return np.hypot(a[0] - b[0], a[1] - b[1])


def hand_size(lm):
    return dist(lm[0], lm[9]) + 1e-6


def fingers_up(lm):
    """[thumb, index, middle, ring, pinky] -> 1 = duoi, 0 = gap."""
    f = [1 if dist(lm[4], lm[5]) > dist(lm[3], lm[5]) * 1.1 else 0]
    for tip, pip in zip((8, 12, 16, 20), (6, 10, 14, 18)):
        f.append(1 if lm[tip][1] < lm[pip][1] else 0)
    return f


def draw_hand(frame, lm):
    h, w, _ = frame.shape
    pts = [(int(x * w), int(y * h)) for x, y in lm]
    for a, b in HAND_CONNECTIONS:
        cv2.line(frame, pts[a], pts[b], (255, 255, 255), 2)
    for p in pts:
        cv2.circle(frame, p, 4, (0, 255, 0), -1)


def show_msg(text):
    S["msg"], S["msg_time"] = text, time.time()


def create_detector():
    if not os.path.exists(MODEL_FILE):
        print("Dang tai model hand_landmarker.task ...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_FILE)
    with open(MODEL_FILE, "rb") as f:          # doc vao bo nho, tranh loi duong dan co dau
        data = f.read()
    options = vision.HandLandmarkerOptions(
        base_options=python.BaseOptions(model_asset_buffer=data),
        running_mode=vision.RunningMode.VIDEO,  # che do video: co tracking nen nhanh hon
        num_hands=1,
        min_hand_detection_confidence=0.6,
        min_hand_presence_confidence=0.6,
        min_tracking_confidence=0.6,
    )
    return vision.HandLandmarker.create_from_options(options)


def open_camera():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) if sys.platform == "win32" else cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_H)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)         # giam do tre
    return cap


# ----------------------------- AM LUONG / DO SANG -----------------------------
def init_volume():
    global volume_ctl
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from comtypes import CLSCTX_ALL
        from ctypes import cast, POINTER
        speakers = AudioUtilities.GetSpeakers()
        if hasattr(speakers, "EndpointVolume"):         # pycaw ban moi
            volume_ctl = speakers.EndpointVolume
        else:                                           # pycaw ban cu
            iface = speakers.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume_ctl = cast(iface, POINTER(IAudioEndpointVolume))
        S["vol"] = S["vol_applied"] = volume_ctl.GetMasterVolumeLevelScalar() * 100
    except Exception as e:
        print("Khong dung duoc pycaw, chuyen sang dung phim volume:", e)


def set_volume(percent):
    if volume_ctl is not None:
        volume_ctl.SetMasterVolumeLevelScalar(percent / 100, None)
        return
    # du phong: bam phim am luong (moi lan ~2%)
    n = int((percent - S["vol_applied"]) / 2)
    n = max(-5, min(5, n))
    for _ in range(abs(n)):
        pyautogui.press("volumeup" if n > 0 else "volumedown")
    S["vol_applied"] += 2 * n


class BrightnessWorker(threading.Thread):
    """Chay nen vi sbc.set_brightness kha cham, tranh lam tut FPS."""
    def __init__(self):
        super().__init__(daemon=True)
        self.target = None
        self.current = None

    def run(self):
        while True:
            t = self.target
            if t is not None and t != self.current:
                try:
                    sbc.set_brightness(t)
                except Exception:
                    pass
                self.current = t
            time.sleep(0.05)


# ----------------------------- CAC CHE DO -----------------------------
def move_cursor(lm):
    x = np.interp(lm[8][0], (MARGIN, 1 - MARGIN), (0, screen_w - 1))
    y = np.interp(lm[8][1], (MARGIN, 1 - MARGIN), (0, screen_h - 1))
    S["prev_x"] += (x - S["prev_x"]) / SMOOTH
    S["prev_y"] += (y - S["prev_y"]) / SMOOTH
    pyautogui.moveTo(S["prev_x"], S["prev_y"])


def mode_mouse(lm, f, size, now):
    thumb, index, middle, ring, pinky = f

    # Ngon cai + giua cham nhau (kem dieu kien ngon giua con "voi ra" de tranh nhan nham
    # khi ngon giua gap sat long ban tay)
    pinch_l = (dist(lm[4], lm[12]) / size < PINCH_RATIO) and (dist(lm[0], lm[12]) / size > 1.15)
    # Ngon tro + ut cham nhau
    pinch_r = dist(lm[8], lm[20]) / size < PINCH_RATIO

    if pinch_r:
        S["status"] = "Right click"
        if not S["pinch_r"] and now - S["last_click"] > CLICK_COOLDOWN:
            pyautogui.click(button="right")
            S["last_click"] = now
        S["pinch_r"], S["pinch_l"] = True, False
        return
    S["pinch_r"] = False

    if pinch_l:
        S["status"] = "Left click"
        if not S["pinch_l"] and now - S["last_click"] > CLICK_COOLDOWN:
            pyautogui.click()
            S["last_click"] = now
        S["pinch_l"] = True
        return
    S["pinch_l"] = False

    if index and not (middle or ring or pinky):
        S["status"] = "Move"
        move_cursor(lm)
    elif middle and not (index or ring or pinky):
        S["status"] = "Scroll UP"
        pyautogui.scroll(SCROLL_AMOUNT)
    elif pinky and not (index or middle or ring):
        S["status"] = "Scroll DOWN"
        pyautogui.scroll(-SCROLL_AMOUNT)
    else:
        S["status"] = "Idle"


def mode_volume(lm, f, size, now):
    thumb, index, middle, ring, pinky = f
    if middle or ring or pinky:                       # chi dung ngon cai + tro
        S["status"] = "Volume: chi dung ngon cai + tro"
        return
    ratio = dist(lm[4], lm[8]) / size
    target = float(np.interp(ratio, VOL_RANGE, (0, 100)))
    S["vol"] += (target - S["vol"]) * 0.4
    set_volume(S["vol"])
    S["status"] = f"Volume {int(S['vol'])}%"


def mode_brightness(lm, f, size, now):
    thumb, index, middle, ring, pinky = f
    if not (index and not (middle or ring or pinky)):
        S["status"] = "Brightness: giu ngon tro"
        return
    target = float(np.interp(lm[8][1], (MARGIN, 1 - MARGIN), (100, 0)))   # tay cang cao cang sang
    S["bright"] += (target - S["bright"]) * 0.3
    S["status"] = f"Brightness {int(S['bright'])}%"
    if brightness_worker is not None:
        brightness_worker.target = int(round(S["bright"] / 2) * 2)


def take_screenshot():
    os.makedirs(SAVE_DIR, exist_ok=True)
    path = os.path.join(SAVE_DIR, time.strftime("screenshot_%Y%m%d_%H%M%S.png"))
    cv2.moveWindow(WIN, -3000, 0)                     # day cua so camera ra ngoai de khong bi chup vao
    cv2.waitKey(250)
    pyautogui.screenshot().save(path)
    cv2.moveWindow(WIN, 50, 50)
    return path


def mode_screenshot(lm, f, size, now):
    thumb, index, middle, ring, pinky = f
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


HANDLERS = {
    "MOUSE": mode_mouse,
    "VOLUME": mode_volume,
    "BRIGHTNESS": mode_brightness,
    "SCREENSHOT": mode_screenshot,
}


# ----------------------------- CHUYỂN CHẾ ĐỘ -----------------------------
def set_mode(name, now):
    S["mode"] = name
    S["selecting"] = False
    S["last_mode_change"] = now
    S["pinch_l"] = S["pinch_r"] = False
    S["v_start"] = None
    show_msg("Mode: " + name)


def update_selection(f, now):
    """Nam tay giu 0.8s -> chon che do bang so ngon. Tra ve True neu dang o trang thai chon."""
    count = sum(f[1:])                                # so ngon tro -> ut dang duoi

    if not S["selecting"]:
        if now - S["last_mode_change"] < 1.0:         # tranh kich hoat lai ngay sau khi doi che do
            S["fist_start"] = None
            return False
        if count == 0:
            if S["fist_start"] is None:
                S["fist_start"] = now
            elif now - S["fist_start"] >= FIST_HOLD:
                S["selecting"], S["fist_start"] = True, None
                S["sel_start"], S["sel_count"] = now, None
        else:
            S["fist_start"] = None
        return S["selecting"]

    # dang o trang thai chon
    S["status"] = "CHON CHE DO: 1=Mouse 2=Volume 3=Bright 4=Shot"
    if now - S["sel_start"] > SELECT_TIMEOUT:         # het thoi gian -> huy
        S["selecting"] = False
        S["last_mode_change"] = now
        return False
    if 1 <= count <= 4:
        if S["sel_count"] != count:
            S["sel_count"], S["sel_hold"] = count, now
        elif now - S["sel_hold"] >= SELECT_HOLD:
            set_mode(MODES[count], now)
    else:
        S["sel_count"] = None
    return True


# ----------------------------- GIAO DIEN -----------------------------
def draw_bar(frame, x, value, label, color):
    h = frame.shape[0]
    top, bottom = 90, h - 40
    cv2.rectangle(frame, (x, top), (x + 25, bottom), (255, 255, 255), 2)
    fill = int(np.interp(value, (0, 100), (bottom, top)))
    cv2.rectangle(frame, (x, fill), (x + 25, bottom), color, -1)
    cv2.putText(frame, label, (x - 5, bottom + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)


def draw_ui(frame, fps):
    h, w, _ = frame.shape
    x1, y1, x2, y2 = int(w * MARGIN), int(h * MARGIN), int(w * (1 - MARGIN)), int(h * (1 - MARGIN))
    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 2)

    cv2.putText(frame, f"MODE: {S['mode']}", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    cv2.putText(frame, S["status"], (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.putText(frame, f"FPS: {int(fps)}", (w - 100, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
    if time.time() - S["msg_time"] < 2:
        cv2.putText(frame, S["msg"], (10, h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)

    if S["mode"] == "VOLUME":
        draw_bar(frame, w - 45, S["vol"], "VOL", (0, 255, 0))
    elif S["mode"] == "BRIGHTNESS":
        draw_bar(frame, w - 45, S["bright"], "BRI", (0, 220, 255))
        if sbc is None:
            cv2.putText(frame, "Chua cai screen-brightness-control", (10, 85),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)


# ----------------------------- VONG LAP CHINH -----------------------------
def main():
    global brightness_worker

    cap = open_camera()
    if not cap.isOpened():
        print("Khong mo duoc camera.")
        return

    detector = create_detector()
    init_volume()
    if sbc is not None:
        brightness_worker = BrightnessWorker()
        brightness_worker.start()

    cv2.namedWindow(WIN)
    cv2.moveWindow(WIN, 50, 50)

    t0 = time.time()
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

        ts = int((time.time() - t0) * 1000)           # timestamp phai tang dan
        if ts <= last_ts:
            ts = last_ts + 1
        last_ts = ts
        result = detector.detect_for_video(mp_img, ts)

        now = time.time()
        if result.hand_landmarks:
            lm = [(p.x, p.y) for p in result.hand_landmarks[0]]
            draw_hand(frame, lm)
            f = fingers_up(lm)
            if not update_selection(f, now):
                HANDLERS[S["mode"]](lm, f, hand_size(lm), now)
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