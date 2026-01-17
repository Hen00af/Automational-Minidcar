import time
# ハードウェアモジュールの自動インポート（Raspberry Pi環境では実機、それ以外ではモック）
from hardware_import import board, busio, digitalio
import adafruit_vl53l0x

# --- 設定：各センサーのXSHUTピンを繋ぐGPIO番号 ---
# ここでは例として GPIO 17, 27, 22 を使います
XSHUT_PINS = [17, 27, 22]

i2c = busio.I2C(board.SCL, board.SDA)

# センサーを格納するリスト
sensors = []
xshut_controls = []

# 1. まず全てのセンサーをリセット状態（Low）にする
for pin_num in XSHUT_PINS:
    # board.D17, board.D27... のように指定
    pin = digitalio.DigitalInOut(getattr(board, f"D{pin_num}"))
    pin.direction = digitalio.Direction.OUTPUT
    pin.value = False
    xshut_controls.append(pin)

time.sleep(0.1)

# 2. 1つずつ順番に起動してアドレスを書き換える
for i, pin in enumerate(xshut_controls):
    pin.value = True  # そのセンサーだけ電源をONにするイメージ
    time.sleep(0.01)

    # 起動直後は 0x29 にいるので、それを捕まえる
    s = adafruit_vl53l0x.VL53L0X(i2c, address=0x29)

    # 重ならないように 0x30, 0x31, 0x32 とアドレスを変えていく
    new_address = 0x30 + i
    s.set_address(new_address)

    sensors.append(s)
    print(f"センサー {i} をアドレス {hex(new_address)} で初期化しました")

# 3. メインループ
print("計測を開始します... (Ctrl+C で終了)")
try:
    while True:
        # 3つのセンサーから順番に値を読み取って表示
        # センサーが少ない/多い場合は自動で対応します
        readings = []
        for i, s in enumerate(sensors):
            readings.append(f"S{i}: {s.range:>4}mm")

        print(" | ".join(readings))
        print(time.time())
        # time.sleep(0.05)

except KeyboardInterrupt:
    print("\n終了します")