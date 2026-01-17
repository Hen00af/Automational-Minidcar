"""
定数定義モジュール
モック実装で使用する定数を集約
"""
from typing import Final

# PWM制御関連の定数
PWM_PERIOD_US: Final[int] = 20000  # PWM周期（20ms = 20000μs @ 50Hz）
DUTY_CYCLE_MAX_VALUE: Final[int] = 65535  # duty_cycle最大値（16bit）

# ロギング関連の定数
DEFAULT_LOG_INTERVAL_SEC: Final[float] = 1.0  # デフォルトのログ出力間隔（秒）

# デフォルトの距離設定（mm）
DEFAULT_LEFT_DISTANCE_MM: Final[float] = 200.0
DEFAULT_FRONT_DISTANCE_MM: Final[float] = 500.0
DEFAULT_RIGHT_DISTANCE_MM: Final[float] = 300.0

# デフォルトのキャリブレーション設定（μs）
DEFAULT_STEER_CENTER_US: Final[int] = 1500
DEFAULT_STEER_LEFT_US: Final[int] = 1300
DEFAULT_STEER_RIGHT_US: Final[int] = 1700
DEFAULT_THROTTLE_STOP_US: Final[int] = 1500
DEFAULT_THROTTLE_MAX_US: Final[int] = 1600

# デフォルトの制御パラメータ
DEFAULT_TARGET_DISTANCE_MM: Final[float] = 200.0
DEFAULT_BASE_SPEED: Final[float] = 0.5

# ループ設定
DEFAULT_LOOP_INTERVAL_SEC: Final[float] = 0.1  # 10Hz
