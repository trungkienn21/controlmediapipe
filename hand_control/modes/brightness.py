import numpy as np

from .. import state
from ..config import MARGIN
from ..media_controls import sbc
from ..state import S


def mode_brightness(landmarks, fingers, size, now):
    _, index, middle, ring, pinky = fingers
    if not (index and not (middle or ring or pinky)):
        S["status"] = "Brightness: giu ngon tro"
        return
    target = float(np.interp(landmarks[8][1], (MARGIN, 1 - MARGIN), (100, 0)))
    S["bright"] += (target - S["bright"]) * 0.3
    S["status"] = f"Brightness {int(S['bright'])}%"
    if state.brightness_worker is not None:
        state.brightness_worker.target = int(round(S["bright"] / 2) * 2)
