# --------------------------------
# config/hardware.py
# ハードウェア関連の設定定数
# --------------------------------
from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class PCA9685Config:
    """PCA9685設定"""
    FREQUENCY: Final[int] = 50  # PWM周波数（ESC/サーボは50Hz）
    I2C_ADDRESS: Final[int] = 0x40  # I2Cアドレス（デフォルト）
    CH_ESC: Final[int] = 0      # ESC（モーター制御）チャンネル
    CH_SERVO: Final[int] = 1    # サーボ（ステアリング）チャンネル
    
    # duty_cycle値（16bit: 0x0000-0xFFFF）
    DUTY_CYCLE_MIN: Final[int] = 0x1000      # 最小値
    DUTY_CYCLE_NEUTRAL: Final[int] = 0x1800  # ニュートラル
    DUTY_CYCLE_MAX: Final[int] = 0x2000      # 最大値
    
    # 計算用定数
    PWM_PERIOD_US: Final[int] = 20000        # PWM周期（20ms = 20000μs @ 50Hz）
    DUTY_CYCLE_MAX_VALUE: Final[int] = 65535  # duty_cycle最大値（16bit）


@dataclass(frozen=True)
class ESCConfig:
    """ESC制御設定（マイクロ秒）"""
    US_NEUTRAL: Final[int] = 1500        # ニュートラル（停止）
    US_FORWARD_SLOW: Final[int] = 1600   # 前進（低速）
    US_REVERSE: Final[int] = 1450        # 後退


@dataclass(frozen=True)
class ServoConfig:
    """サーボ制御設定（マイクロ秒）"""
    US_LEFT: Final[int] = 1300    # 左
    US_CENTER: Final[int] = 1500   # 中央
    US_RIGHT: Final[int] = 1700    # 右


@dataclass(frozen=True)
class HardwareConfig:
    """ハードウェア設定の集約"""
    pca9685: PCA9685Config = PCA9685Config()
    esc: ESCConfig = ESCConfig()
    servo: ServoConfig = ServoConfig()


# シングルトンインスタンス
hardware = HardwareConfig()
