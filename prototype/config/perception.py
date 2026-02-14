# --------------------------------
# config/perception.py
# 知覚モジュール関連の設定定数
# --------------------------------
from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class CorridorPerceptionConfig:
    """回廊走行知覚モジュール設定"""

    FRONT_BLOCKED_THRESHOLD_MM: Final[float] = (
        700.0  # 前方が障害物と判定する距離の閾値（mm）
    )
    FRONT_SLOW_THRESHOLD_MM: Final[float] = (
        1500.0  # 前方減速を開始する距離の閾値（mm）
    )
    WALL_DETECTION_THRESHOLD_MM: Final[float] = (
        2000.0  # 壁を検知する最大距離（mm）。これ以上は壁なしとみなす
    )
    CORNER_IMBALANCE_RATIO: Final[float] = (
        2.0  # コーナー予測を発動する左右距離比の閾値（片側が何倍以上開いているか）
    )
    CORNER_NEAR_WALL_THRESHOLD_MM: Final[float] = (
        800.0  # コーナー予測の前提条件：近い壁までの距離閾値（mm）
    )


@dataclass(frozen=True)
class PerceptionConfig:
    """知覚モジュール設定の集約"""

    corridor: CorridorPerceptionConfig = CorridorPerceptionConfig()


# シングルトンインスタンス
perception = PerceptionConfig()
