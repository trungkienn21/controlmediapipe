import numpy as np

from ..config import VOL_RANGE
from ..hand_utils import dist
from ..media_controls import set_volume
from ..state import S


def mode_volume(landmarks, fingers, size, now):
    _, _, middle, ring, pinky = fingers
    if middle or ring or pinky:
        S["status"] = "Volume: chi dung ngon cai + tro"
        return
    ratio = dist(landmarks[4], landmarks[8]) / size
    target = float(np.interp(ratio, VOL_RANGE, (0, 100)))
    S["vol"] += (target - S["vol"]) * 0.4
    set_volume(S["vol"])
    S["status"] = f"Volume {int(S['vol'])}%"
