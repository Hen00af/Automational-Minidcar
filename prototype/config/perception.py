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
        2000.0  # 前方減速を開始する距離の閾値（mm）。慣性を考慮し早めに減速開始
    )
    WALL_DETECTION_THRESHOLD_MM: Final[float] = (
        1000.0  # 壁を検知する最大距離（mm）。道幅1mに適合。これ以上は壁なしとみなす
    )
    WALL_TARGET_DISTANCE_MM: Final[float] = (
        707.0  # 道幅1mの中央での45°センサー期待距離（mm）。片側壁なし時の補完用
    )
    SIDE_SLOW_THRESHOLD_MM: Final[float] = (
        400.0  # 側方距離がこれ以下で減速開始（mm）
    )


@dataclass(frozen=True)
class PerceptionConfig:
    """知覚モジュール設定の集約"""

    corridor: CorridorPerceptionConfig = CorridorPerceptionConfig()


# シングルトンインスタンス
perception = PerceptionConfig()
