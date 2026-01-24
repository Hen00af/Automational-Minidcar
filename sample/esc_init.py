import time
# ハードウェアモジュールの自動インポート（Raspberry Pi環境では実機、それ以外ではモック）
from hardware_import import board, busio
from adafruit_pca9685 import PCA9685

i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c)
pca.frequency = 50

ch = pca.channels[0]

# 初期化
print("1. max")
ch.duty_cycle = 0x2000
time.sleep(3)
print("esc switch on")
time.sleep(5)
# 最小値
print("2. min")
ch.duty_cycle = 0x1000
time.sleep(5)
# ニュートラル
print("3. nutral")
ch.duty_cycle = 0x1800
time.sleep(5)

print("comlete")