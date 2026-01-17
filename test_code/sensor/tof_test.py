import time
# ハードウェアモジュールの自動インポート（Raspberry Pi環境では実機、それ以外ではモック）
from hardware_import import board, busio
import adafruit_vl53l0x

i2c = busio.I2C(board.SCL, board.SDA)
tof = adafruit_vl53l0x.VL53L0X(i2c)

while True:
        print(tof.range, "mm")
        time.sleep(0.5)