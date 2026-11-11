import pyautogui


pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0
screen_w, screen_h = pyautogui.size()
mouse_x, mouse_y = pyautogui.position()

S = {
    "mode": "MOUSE", "status": "", "msg": "", "msg_time": 0.0,
    "selecting": False, "fist_start": None, "sel_start": 0.0,
    "sel_count": None, "sel_hold": 0.0, "last_mode_change": 0.0,
    "prev_x": mouse_x, "prev_y": mouse_y,
    "pinch_l": False, "pinch_r": False, "last_click": 0.0,
    "vol": 50.0, "vol_applied": 50.0, "bright": 50.0,
    "v_start": None, "last_shot": 0.0,
}

volume_ctl = None
brightness_worker = None
