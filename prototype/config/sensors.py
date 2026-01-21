# --------------------------------
# config/sensors.py
# センサー関連の設定定数
# --------------------------------
from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Tuple


@dataclass(frozen=True)
class VL53L0XConfig:
    """VL53L0X距離センサー設定"""
    # XSHUTピン番号（GPIO）- 前、左、右の順
    XSHUT_PINS: Final[Tuple[int, int, int]] = (17, 27, 22)
    
    # I2Cアドレス
    DEFAULT_ADDRESS: Final[int] = 0x29      # デフォルトアドレス
    BASE_ADDRESS: Final[int] = 0x30       # マルチセンサー時のベースアドレス
    I2C_ADDRESSES: Final[Tuple[int, int, int]] = (0x30, 0x31, 0x32)  # 前、左、右の順


@dataclass(frozen=True)
class SensorConfig:
    """センサー設定の集約"""
    vl53l0x: VL53L0XConfig = VL53L0XConfig()


# シングルトンインスタンス
sensors = SensorConfig()
