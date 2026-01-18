import time
# ハードウェアモジュールの自動インポート（Raspberry Pi環境では実機、それ以外ではモック）
from hardware_import import board, busio
from adafruit_pca9685 import PCA9685

i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c)
pca.frequency = 50

pca.channels[0].duty_cycle = 0x1800
print("ch[0]:0x1800")
time.sleep(3)
pca.channels[0].duty_cycle = 0x1900
print("ch[0]:0x1900")
time.sleep(1)
pca.channels[0].duty_cycle = 0x1800
print("ch[0]:0x1800")
time.sleep(1)

pca.channels[1].duty_cycle = 0x1000
print("ch[1]:0x1000")
time.sleep(1)
pca.channels[1].duty_cycle = 0x2000
print("ch[1]:0x2000")
time.sleep(1)