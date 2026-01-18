# --------------------------------
# config/utils.py
# 設定関連のユーティリティ関数
# --------------------------------
from __future__ import annotations

import os
import sys
import time
from typing import Optional

from .hardware import hardware

# ハードウェアモジュールのインポート（実機環境を優先、失敗時はモックを使用）
try:
    import board
    import busio
    from adafruit_pca9685 import PCA9685
except (ImportError, RuntimeError):
    # Docker環境などで実機モジュールが使用できない場合はモックを使用
    # test_codeディレクトリをパスに追加
    test_code_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'test_code')
    if test_code_path not in sys.path:
        sys.path.insert(0, test_code_path)
    
    import board_mock as board
    import busio_mock as busio
    import pca9685_mock
    PCA9685 = pca9685_mock.PCA9685
    print("[INFO] Using mock hardware modules for config utils", file=sys.stderr)


def set_us(ch, us: int) -> None:
    """
    μs（マイクロ秒）をduty_cycle値に変換してPCA9685のチャンネルに設定する関数。
    
    Args:
        ch: PCA9685のチャンネルオブジェクト（duty_cycle属性を持つ）
        us: パルス幅（マイクロ秒）
    """
    duty_cycle = int(us / hardware.pca9685.PWM_PERIOD_US * hardware.pca9685.DUTY_CYCLE_MAX_VALUE)
    ch.duty_cycle = duty_cycle


def initialize_pca9685(i2c_address: int = 0x40) -> tuple[PCA9685, any, any]:
    """
    PCA9685を初期化してESCとサーボのチャンネルを返す
    
    Args:
        i2c_address: PCA9685のI2Cアドレス（デフォルト: 0x40）
    
    Returns:
        (pca, esc_channel, servo_channel) のタプル
    """
    i2c = busio.I2C(board.SCL, board.SDA)
    pca = PCA9685(i2c, address=i2c_address)
    pca.frequency = hardware.pca9685.FREQUENCY  # ESC/サーボは50Hz
    
    esc = pca.channels[hardware.pca9685.CH_ESC]    # ESC
    servo = pca.channels[hardware.pca9685.CH_SERVO]  # サーボ
    
    return pca, esc, servo


def test_drive_forward() -> None:
    """
    前進テストを実行（drive_test.pyの1-33行目の内容）
    """
    print("=== 前進 + サーボ + 後退 テスト開始 ===")
    
    # 初期化
    pca, esc, servo = initialize_pca9685()
    
    # ① 停止（ニュートラル）
    print("ESC: Neutral (停止)")
    set_us(esc, hardware.esc.US_NEUTRAL)  # 1500μs
    time.sleep(2)
    
    # ② ゆっくり前進
    print("ESC: Forward slow (1600)")
    set_us(esc, hardware.esc.US_FORWARD_SLOW)
    time.sleep(2)
