from .config import FIST_HOLD, MODES, SELECT_HOLD, SELECT_TIMEOUT
from .hand_utils import show_msg
from .state import S


def set_mode(name, now):
    S["mode"] = name
    S["selecting"] = False
    S["last_mode_change"] = now
    S["pinch_l"] = S["pinch_r"] = False
    S["v_start"] = None
    show_msg("Mode: " + name)


def update_selection(fingers, now):
    """Nam tay giu 0.8s -> chon che do bang so ngon. Tra ve True neu dang o trang thai chon."""
    count = sum(fingers[1:])

    if not S["selecting"]:
        if now - S["last_mode_change"] < 1.0:
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

    S["status"] = "CHON CHE DO: 1=Mouse 2=Volume 3=Bright 4=Shot"
    if now - S["sel_start"] > SELECT_TIMEOUT:
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
