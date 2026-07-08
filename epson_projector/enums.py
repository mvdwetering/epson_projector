

from enum import StrEnum, unique

@unique
class KeyCodes(StrEnum):
    """Epson projector key codes."""

    POWER = "3B"
    POWER_ON = "A1"
    POWER_OFF = "6C"
    MENU = "3C"
    HOME = "30"
    ESC = "3D"
    ENTER = "49"
    POINTER_UP = "58"
    POINTER_DOWN = "59"
    POINTER_LEFT = "5A"
    POINTER_RIGHT = "5B"
    PAGE_UP = "68"
    PAGE_DOWN = "69"
    KEY_0 = "70"
    KEY_1 = "71"
    KEY_2 = "72"
    KEY_3 = "73"
    KEY_4 = "74"
    KEY_5 = "75"
    KEY_6 = "76"
    KEY_7 = "77"
    KEY_8 = "78"
    KEY_9 = "79"
