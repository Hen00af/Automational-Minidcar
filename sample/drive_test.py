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
servo = pca.channels[1]  # サーボ

# μs → duty_cycle 変換
def set_us(ch, us):
    ch.duty_cycle = int(us / 20000 * 65535)

print("=== 前進 + サーボ + 後退 テスト開始 ===")

# --------------------------
# ① 停止（ニュートラル）
# --------------------------
print("ESC: Neutral (停止)")
set_us(esc, 1500)  # 1500μs
time.sleep(2)
# --------------------------
# ② ゆっくり前進
# --------------------------
print("ESC: Forward slow (1600)")
set_us(esc, 1600)
time.sleep(2)

# --------------------------
# ③ サーボ の左右動作
# --------------------------
print("Servo: Left")
set_us(servo, 1300)  # 左
time.sleep(1)

print("Servo: Center")
set_us(servo, 1500)  # 中央
time.sleep(1)

print("Servo: Right")
set_us(servo, 1700)  # 右
time.sleep(1)

print("Servo: Center")
set_us(servo, 1500)
time.sleep(1)

# --------------------------
# ④ 停止
# --------------------------
print("ESC: Neutral (停止)")
set_us(esc, 1500)
time.sleep(2)

# --------------------------
# ⑤ 後退
# --------------------------
print("ESC: Reverse (1450)")
set_us(esc, 1450)
time.sleep(2)

# --------------------------
# ⑥ 停止
# --------------------------
print("ESC: Stop again")
set_us(esc, 1500)
time.sleep(2)

print("=== テスト終了 ===")
