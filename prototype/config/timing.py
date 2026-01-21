# --------------------------------
# config/timing.py
# タイミング関連の設定定数
# --------------------------------
from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class SensorInitTiming:
    """センサー初期化タイミング（秒）"""
    RESET_WAIT: Final[float] = 0.1  # リセット後の待機時間
    WAKE_WAIT: Final[float] = 0.01  # 起動後の待機時間


@dataclass(frozen=True)
class TestTiming:
    """動作テストタイミング（秒）"""
    MOVE_WAIT: Final[float] = 2  # 動作テスト時の待機時間


@dataclass(frozen=True)
class TimingConfig:
    """タイミング設定の集約"""
    sensor_init: SensorInitTiming = SensorInitTiming()
    test: TestTiming = TestTiming()


# シングルトンインスタンス
timing = TimingConfig()
