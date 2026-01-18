import time
# ハードウェアモジュールの自動インポート（Raspberry Pi環境では実機、それ以外ではモック）
from hardware_import import board, busio
from adafruit_pca9685 import PCA9685
from const import (
    PCA9685_FREQUENCY,
    CH_ESC,
    CH_SERVO,
    ESC_US_NEUTRAL,
    ESC_US_FORWARD_SLOW,
    SERVO_US_CENTER,
    TEST_MOVE_WAIT,
    TEST_SERVO_WAIT,
    PWM_PERIOD_US,
    DUTY_CYCLE_MAX_VALUE,
)

# --------------------------
# 初期化
# --------------------------
i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c)
pca.frequency = PCA9685_FREQUENCY

esc = pca.channels[CH_ESC]    # ESC
servo = pca.channels[CH_SERVO]  # サーボ

# μs → duty_cycle 変換
def set_us(ch, us):
    ch.duty_cycle = int(us / PWM_PERIOD_US * DUTY_CYCLE_MAX_VALUE)

print("=== まっすぐ進むテスト開始 ===")

# --------------------------
# ① サーボを中央に設定（まっすぐ進むため）
# --------------------------
print("Servo: Center (中央)")
set_us(servo, SERVO_US_CENTER)
time.sleep(TEST_SERVO_WAIT)

# --------------------------
# ② 停止（ニュートラル）
# --------------------------
print("ESC: Neutral (停止)")
set_us(esc, ESC_US_NEUTRAL)
time.sleep(TEST_MOVE_WAIT)

# --------------------------
# ③ まっすぐ前進
# --------------------------
print("ESC: Forward slow (前進)")
set_us(esc, ESC_US_FORWARD_SLOW)
time.sleep(TEST_MOVE_WAIT)

# --------------------------
# ④ 停止
# --------------------------
print("ESC: Neutral (停止)")
set_us(esc, ESC_US_NEUTRAL)
time.sleep(TEST_MOVE_WAIT)

print("=== テスト終了 ===")
