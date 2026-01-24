import time
# ハードウェアモジュールの自動インポート（Raspberry Pi環境では実機、それ以外ではモック）
from hardware_import import board, busio
from adafruit_pca9685 import PCA9685

# --------------------------
# 初期化
# --------------------------
i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c)
pca.frequency = 50  # ESC/サーボは50Hz

esc = pca.channels[0]    # ESC

# μs → duty_cycle 変換
def set_us(ch, us):
    ch.duty_cycle = int(us / 20000 * 65535)

print("=== PWM可変テスト開始 ===")
print("1500μsから1000μsまで可変で送信します")

# 初期値を1500μsに設定
print("ESC: 初期値 1500μs")
set_us(esc, 1500)
time.sleep(2)

# 1500から1000まで10ずつ減らしていく
for us_value in range(1500, 0, -10):  # 1500から0まで10ずつ減らす
    print(f"ESC: {us_value}μs")
    set_us(esc, us_value)
    time.sleep(1)  # 各値で1秒待機

# 最後に1000μsを設定
print("ESC: 1000μs")
set_us(esc, 1000)
time.sleep(2)

# 停止（ニュートラルに戻す）
print("ESC: Neutral (1500μs) に戻す")
set_us(esc, 1500)
time.sleep(2)

print("=== テスト終了 ===")
