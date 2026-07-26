from __future__ import annotations

from enum import StrEnum, unique
import logging

_LOGGER = logging.getLogger(__name__)

@unique
class KeyCodes(StrEnum):
    """Epson projector key codes."""

    POWER = "3B"
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
    POWER_OFF = "6C"
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
    DEFAULT = "88"
    POWER_ON = "A1"

class PowerStatus(StrEnum):
    """Power status of the projector."""

    STANDBY = "00"
    """Standby Mode"""
    NORMAL = "01"
    """Normal status"""
    WARMUP = "02"
    """Warmup"""
    COOLDOWN = "03"
    """Cool down"""
    STANDBY_NETWORK = "04"
    """Standby Mode  (Network ON) / Communication Standby"""
    ABNORMAL_STANDBY = "05"
    """Abnormality standby"""
    AV_OR_USB_POWER_STANDBY = "09"
    """A/V standby / USB power standby"""

    _UNKNOWN = "??"
    """Unknown in case unsupported value is returned by projector."""

    @classmethod
    def _missing_(cls, value: object) -> PowerStatus:
        _LOGGER.warning("Unknown value '%s' for %s", value, cls.__name__)
        return cls._UNKNOWN

class CMode(StrEnum):
    """Color mode of the projector."""

    AUTO = "00"
    """Auto"""
    THEATRE = "05"
    """Theatre"""
    DYNAMIC = "06"
    """Dynamic"""
    NATURAL = "07"
    """Natural"""
    THEATRE_BLACK_1_HD = "09"
    """Theatre Black 1/HD"""
    THEATRE_BLACK_2_SILVER_SCREEN = "0A"
    """Theatre Black 2/Silver Screen"""
    X_V_COLOR = "0B"
    """x.v. color"""
    BRIGHT_CINEMA = "0C"
    """Bright Cinema"""
    GAME = "0D"
    """Game"""
    THX = "13"
    """THX"""
    CINEMA = "15"
    """Cinema"""
    STAGE = "16"
    """Stage"""
    THREE_D_CINEMA = "17"
    """3D Cinema"""
    THREE_D_DYNAMIC = "18"
    """3D Dynamic"""
    THREE_D_THX = "19"
    """3D THX"""
    B_W_CINEMA = "20"
    """B&W Cinema"""
    ADOBE_RGB = "21"
    """Adobe RGB"""
    DIGITAL_CINEMA = "22"
    """Digital Cinema"""
    VIVID = "23"
    """Vivid"""
    AUTO_COLOR = "C1"
    """AutoColor"""

    _UNKNOWN = "??"
    """Unknown in case unsupported value is returned by projector."""

    @classmethod
    def _missing_(cls, value: object) -> CMode:
        _LOGGER.warning("Unknown value '%s' for %s", value, cls.__name__)
        return cls._UNKNOWN

class Source(StrEnum):
    """Input source of the projector."""

    PC = "10"
    """PC"""
    HDMI1 = "30"
    """HDMI 1"""
    VIDEO = "40"
    """Video"""
    SVIDEO = "41"
    """S-Video"""
    USB = "52"
    """USB"""
    LAN = "53"
    """LAN"""
    WFD = "56"
    """WiFi Direct"""
    HDMI2 = "A0"
    """HDMI 2"""

    _UNKNOWN = "??"
    """Unknown in case unsupported value is returned by projector."""

    @classmethod
    def _missing_(cls, value: object) -> Source:
        _LOGGER.warning("Unknown value '%s' for %s", value, cls.__name__)
        return cls._UNKNOWN
