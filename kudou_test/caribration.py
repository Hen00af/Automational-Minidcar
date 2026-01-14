import time
import board
import busio
from adafruit_pca9685 import PCA9685

i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c)
pca.frequency = 50

ch = pca.channels[0]

print("max")
ch.duty_cycle = 0x2000
time.sleep(3)

print("min")
ch.duty_cycle = 0x1000
time.sleep(3)

print("complete")