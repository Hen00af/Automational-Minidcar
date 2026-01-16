"""
定数定義ファイル
"""

# ====================
# PCA9685関連
# ====================
# PWM周波数（ESC/サーボは50Hz）
PCA9685_FREQUENCY = 50

# チャンネル番号
CH_ESC = 0      # ESC（モーター制御）
CH_SERVO = 1    # サーボ（ステアリング）

# duty_cycle値（16bit: 0x0000-0xFFFF）
DUTY_CYCLE_MIN = 0x1000      # 最小値
DUTY_CYCLE_NEUTRAL = 0x1800  # ニュートラル
DUTY_CYCLE_MAX = 0x2000      # 最大値

# ====================
# ESC制御（マイクロ秒）
# ====================
ESC_US_NEUTRAL = 1500  # ニュートラル（停止）
ESC_US_FORWARD_SLOW = 1600  # 前進（低速）
ESC_US_REVERSE = 1450  # 後退

# ====================
# サーボ制御（マイクロ秒）
# ====================
SERVO_US_LEFT = 1300   # 左
SERVO_US_CENTER = 1500 # 中央
SERVO_US_RIGHT = 1700  # 右

# ====================
# VL53L0X距離センサー関連
# ====================
# XSHUTピン番号（GPIO）
XSHUT_PINS = [17, 27, 22]

# I2Cアドレス
VL53L0X_DEFAULT_ADDRESS = 0x29  # デフォルトアドレス
VL53L0X_BASE_ADDRESS = 0x30     # マルチセンサー時のベースアドレス

# ====================
# タイミング定数（秒）
# ====================
# ESC初期化
ESC_INIT_MAX_WAIT = 3      # 最大値設定後の待機時間
ESC_INIT_SWITCH_WAIT = 5   # ESCスイッチON後の待機時間
ESC_INIT_MIN_WAIT = 5      # 最小値設定後の待機時間
ESC_INIT_NEUTRAL_WAIT = 5  # ニュートラル設定後の待機時間

# センサー初期化
SENSOR_RESET_WAIT = 0.1    # リセット後の待機時間
SENSOR_WAKE_WAIT = 0.01    # 起動後の待機時間

# 動作テスト
TEST_MOVE_WAIT = 2         # 動作テスト時の待機時間
TEST_SERVO_WAIT = 1        # サーボ動作時の待機時間

# ====================
# 計算用定数
# ====================
# PWM周期（20ms = 20000μs @ 50Hz）
PWM_PERIOD_US = 20000
# duty_cycle最大値（16bit）
DUTY_CYCLE_MAX_VALUE = 65535
