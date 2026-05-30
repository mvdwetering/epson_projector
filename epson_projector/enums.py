"""Enum definitions for Epson projector."""

from enum import StrEnum


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
    DYNAMIC = "06"
    NATURAL = "07"
    XV_COLOR = "0B"
    BRIGHT_CINEMA = "0C"
    CINEMA = "15"
    BW_CINEMA = "20"
    VIVID = "23"    
    
