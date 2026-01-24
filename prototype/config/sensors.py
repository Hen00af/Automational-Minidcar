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
    
    # センサー設定
    NUM_SENSORS: Final[int] = 3  # センサーの数（前、左、右）
    MEASUREMENT_TIMING_BUDGET: Final[int] = 20000  # 計測時間バジェット（マイクロ秒）。小さいほど高速だが精度が下がる
    SENSOR_NAMES: Final[Tuple[str, ...]] = ("前", "左", "右")  # センサー名（順序はXSHUT_PINSと対応）


@dataclass(frozen=True)
class SensorConfig:
    """センサー設定の集約"""
    vl53l0x: VL53L0XConfig = VL53L0XConfig()


# シングルトンインスタンス
sensors = SensorConfig()
