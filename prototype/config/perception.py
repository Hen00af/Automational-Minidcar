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
        500.0  # 前方が障害物と判定する距離の閾値（mm）
    )
    FRONT_SLOW_THRESHOLD_MM: Final[float] = (
        1000.0  # 前方減速を開始する距離の閾値（mm）
    )
    WALL_DETECTION_THRESHOLD_MM: Final[float] = (
        2000.0  # 壁を検知する最大距離（mm）。これ以上は壁なしとみなす
    )

    # Y字分岐検知用の閾値
    FORK_FRONT_THRESHOLD_MM: Final[float] = (
        600.0  # 正面が壁を検知する距離（mm）。分岐の島を検知
    )
    FORK_SIDE_OPEN_THRESHOLD_MM: Final[float] = (
        800.0  # 左右が「開けている」と判定する距離（mm）。通路方向を検知
    )


@dataclass(frozen=True)
class PerceptionConfig:
    """知覚モジュール設定の集約"""

    corridor: CorridorPerceptionConfig = CorridorPerceptionConfig()


# シングルトンインスタンス
perception = PerceptionConfig()
