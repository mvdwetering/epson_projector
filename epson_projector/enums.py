"""Enum definitions for Epson projector."""

from enum import StrEnum
import logging


class PowerStatus(StrEnum):
    """Power status of the projector."""

    # 00: Standby Mode
    # 01: Normal status
    # 02: Warmup
    # 03: Cool down
    # 04: Standby Mode  (Network ON) / Communication Standby
    # 05: Abnormality standby
    # 09: A/V standby / USB power standby

    STANDBY = "00"
    NORMAL = "01"
    WARMUP = "02"
    COOLDOWN = "03"
    STANDBY_NETWORK = "04"
    ABNORMALITY = "05"
    AV_STANDBY = "09"


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
    @classmethod
    def _missing_(cls, value: object) -> "CMode":
        logging.warning("Unknown value '%s' for %s", value, cls.__name__)
        return cls._UNKNOWN

class Source(StrEnum):
    """Input source of the projector."""

    HDMI1 = "30"
    """HDMI 1"""
    PC = "10"
    """PC"""
    VIDEO = "40"
    """Video"""
    USB = "52"
    """USB"""
    LAN = "53"
    """LAN"""
    WDF = "56"
    """WiFi Direct"""
    HDMI2 = "A0"
    """HDMI 2"""
    VIDEO2 = "41"
    """Video 2"""

    _UNKNOWN = "??"
    @classmethod
    def _missing_(cls, value: object) -> "Source":
        logging.warning("Unknown value '%s' for %s", value, cls.__name__)
        return cls._UNKNOWN
