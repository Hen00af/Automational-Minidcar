# --------------------------------
# actuation.py
# --------------------------------
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


@dataclass(frozen=True)
class ActuationCalibration:
    """
    Command(正規化値) -> 実機信号(PWM等)への写像ルール（定数/設定）。
    ※第1イテレーションでは値は仮でも、I/Fとして分離しておく。
    """
    # steering servo
    steer_center_us: int
    steer_left_us: int     # steer=+1.0
    steer_right_us: int    # steer=-1.0

    # throttle (ESC)
    throttle_stop_us: int
    throttle_max_us: int   # throttle=+1.0

    # optional limits (safety clamp)
    steer_limit: float = 1.0
    throttle_limit: float = 1.0


class ActuationStatus(str, Enum):
    OK = "OK"
    STOPPED = "STOPPED"
    DRIVER_ERROR = "DRIVER_ERROR"
    CALIBRATION_ERROR = "CALIBRATION_ERROR"


@dataclass(frozen=True)
class Telemetry:
    """
    Actuation の適用結果（ログ/デバッグ向け）。
    """
    frame_id: int
    t_capture_sec: float

    status: ActuationStatus
    applied_steer: Optional[float] = None
    applied_throttle: Optional[float] = None

    steer_pwm_us: Optional[int] = None
    throttle_pwm_us: Optional[int] = None

    message: Optional[str] = None

