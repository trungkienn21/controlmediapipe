from .brightness import mode_brightness
from .mouse import mode_mouse
from .screenshot import mode_screenshot
from .volume import mode_volume


HANDLERS = {
    "MOUSE": mode_mouse,
    "VOLUME": mode_volume,
    "BRIGHTNESS": mode_brightness,
    "SCREENSHOT": mode_screenshot,
}
