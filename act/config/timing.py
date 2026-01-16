# --------------------------------
# config/timing.py
# タイミング関連の設定定数
# --------------------------------
from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class ESCInitTiming:
    """ESC初期化タイミング（秒）"""
    MAX_WAIT: Final[float] = 3      # 最大値設定後の待機時間
    SWITCH_WAIT: Final[float] = 5  # ESCスイッチON後の待機時間
    MIN_WAIT: Final[float] = 5     # 最小値設定後の待機時間
    NEUTRAL_WAIT: Final[float] = 5 # ニュートラル設定後の待機時間


@dataclass(frozen=True)
class SensorInitTiming:
    """センサー初期化タイミング（秒）"""
    RESET_WAIT: Final[float] = 0.1  # リセット後の待機時間
    WAKE_WAIT: Final[float] = 0.01  # 起動後の待機時間


@dataclass(frozen=True)
class TestTiming:
    """動作テストタイミング（秒）"""
    MOVE_WAIT: Final[float] = 2  # 動作テスト時の待機時間
    SERVO_WAIT: Final[float] = 1  # サーボ動作時の待機時間


@dataclass(frozen=True)
class TimingConfig:
    """タイミング設定の集約"""
    esc_init: ESCInitTiming = ESCInitTiming()
    sensor_init: SensorInitTiming = SensorInitTiming()
    test: TestTiming = TestTiming()


# シングルトンインスタンス
timing = TimingConfig()
