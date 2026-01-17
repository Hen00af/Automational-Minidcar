# --------------------------------
# config/utils.py
# 設定関連のユーティリティ関数
# --------------------------------
from __future__ import annotations

from .hardware import hardware


def set_us(ch, us: int) -> None:
    """
    μs（マイクロ秒）をduty_cycle値に変換してPCA9685のチャンネルに設定する関数。
    
    Args:
        ch: PCA9685のチャンネルオブジェクト（duty_cycle属性を持つ）
        us: パルス幅（マイクロ秒）
    """
    duty_cycle = int(us / hardware.pca9685.PWM_PERIOD_US * hardware.pca9685.DUTY_CYCLE_MAX_VALUE)
    ch.duty_cycle = duty_cycle
