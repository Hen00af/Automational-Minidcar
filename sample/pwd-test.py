import sys
import time
from pathlib import Path

# prototypeモジュールをインポートできるようにパスを追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# prototypeの設定とユーティリティをインポート
from prototype.config import hardware, timing
from prototype.config.utils import set_us, initialize_pca9685

print("=== PWM可変テスト開始 ===")
print("1500μsから1000μsまで可変で送信します")

# --------------------------
# 初期化（prototypeのパターンを使用）
# --------------------------
pca, esc, servo = initialize_pca9685()

# 初期値を1500μs（ニュートラル）に設定
print(f"ESC: 初期値 {hardware.esc.US_NEUTRAL}μs (ニュートラル)")
set_us(esc, hardware.esc.US_NEUTRAL)
time.sleep(timing.test.MOVE_WAIT)

# 1500から1000まで10ずつ減らしていく
for us_value in range(1500, 990, -10):  # 1500から1000まで10ずつ減らす
    print(f"ESC: {us_value}μs")
    set_us(esc, us_value)
    time.sleep(1)  # 各値で1秒待機

# 最後に1000μsを設定
print("ESC: 1000μs")
set_us(esc, 1000)
time.sleep(timing.test.MOVE_WAIT)

# 停止（ニュートラルに戻す）
print(f"ESC: Neutral ({hardware.esc.US_NEUTRAL}μs) に戻す")
set_us(esc, hardware.esc.US_NEUTRAL)
time.sleep(timing.test.MOVE_WAIT)

print("=== テスト終了 ===")
