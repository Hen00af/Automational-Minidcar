# config パッケージ
# ハードウェア設定とユーティリティ関数を提供

from .hardware import HardwareConfig, hardware
from .sensors import SensorConfig, sensors
from .timing import TimingConfig, timing
from .utils import set_us
from .constants import (
    PWM_PERIOD_US,
    DUTY_CYCLE_MAX_VALUE,
    DEFAULT_LOG_INTERVAL_SEC,
    DEFAULT_LEFT_DISTANCE_MM,
    DEFAULT_FRONT_DISTANCE_MM,
    DEFAULT_RIGHT_DISTANCE_MM,
    DEFAULT_STEER_CENTER_US,
    DEFAULT_STEER_LEFT_US,
    DEFAULT_STEER_RIGHT_US,
    DEFAULT_THROTTLE_STOP_US,
    DEFAULT_THROTTLE_MAX_US,
    DEFAULT_TARGET_DISTANCE_MM,
    DEFAULT_BASE_SPEED,
    DEFAULT_LOOP_INTERVAL_SEC,
)

__all__ = [
    "HardwareConfig",
    "hardware",
    "SensorConfig",
    "sensors",
    "TimingConfig",
    "timing",
    "set_us",
    # Constants
    "PWM_PERIOD_US",
    "DUTY_CYCLE_MAX_VALUE",
    "DEFAULT_LOG_INTERVAL_SEC",
    "DEFAULT_LEFT_DISTANCE_MM",
    "DEFAULT_FRONT_DISTANCE_MM",
    "DEFAULT_RIGHT_DISTANCE_MM",
    "DEFAULT_STEER_CENTER_US",
    "DEFAULT_STEER_LEFT_US",
    "DEFAULT_STEER_RIGHT_US",
    "DEFAULT_THROTTLE_STOP_US",
    "DEFAULT_THROTTLE_MAX_US",
    "DEFAULT_TARGET_DISTANCE_MM",
    "DEFAULT_BASE_SPEED",
    "DEFAULT_LOOP_INTERVAL_SEC",
]
