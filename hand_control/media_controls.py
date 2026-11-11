import threading
import time

import pyautogui

from . import state
from .state import S

try:
    import screen_brightness_control as sbc
except ImportError:
    sbc = None


def init_volume():
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from comtypes import CLSCTX_ALL
        from ctypes import POINTER, cast

        speakers = AudioUtilities.GetSpeakers()
        if hasattr(speakers, "EndpointVolume"):
            state.volume_ctl = speakers.EndpointVolume
        else:
            interface = speakers.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            state.volume_ctl = cast(interface, POINTER(IAudioEndpointVolume))
        S["vol"] = S["vol_applied"] = state.volume_ctl.GetMasterVolumeLevelScalar() * 100
    except Exception as error:
        print("Khong dung duoc pycaw, chuyen sang dung phim volume:", error)


def set_volume(percent):
    if state.volume_ctl is not None:
        state.volume_ctl.SetMasterVolumeLevelScalar(percent / 100, None)
        return
    steps = int((percent - S["vol_applied"]) / 2)
    steps = max(-5, min(5, steps))
    for _ in range(abs(steps)):
        pyautogui.press("volumeup" if steps > 0 else "volumedown")
    S["vol_applied"] += 2 * steps


class BrightnessWorker(threading.Thread):
    """Chay nen vi sbc.set_brightness kha cham, tranh lam tut FPS."""

    def __init__(self):
        super().__init__(daemon=True)
        self.target = None
        self.current = None

    def run(self):
        while True:
            target = self.target
            if target is not None and target != self.current:
                try:
                    sbc.set_brightness(target)
                except Exception:
                    pass
                self.current = target
            time.sleep(0.05)
