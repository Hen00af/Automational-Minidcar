import time
import board
import busio
from adafruit_pca9685 import PCA9685

i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c)
pca.frequency = 50

esc = pca.channels[0]

print("=== QuicRun 1060 Calibration ===")
print("ESC switch OFF")

time.sleep(2)

print("Send MAX (2000us)")
esc.duty_cycle = 0x1999   # ← 正しい MAX

print(">>> TURN ESC SWITCH ON NOW <<<")
time.sleep(8)             # この間にESCをON

print("Send NEUTRAL (1500us)")
esc.duty_cycle = 0x1333   # ← 正しい ニュートラル
time.sleep(3)

print("Calibration finished")
print("Turn ESC OFF, then ON again")