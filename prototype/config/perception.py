# --------------------------------
# config/perception.py
# 知覚モジュール関連の設定定数
# --------------------------------
from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class WallPositionPerceptionConfig:
    """壁位置知覚モジュール設定"""
    TARGET_DISTANCE_MM: Final[float] = 500.0  # 左壁との目標距離（mm）
    FRONT_BLOCKED_THRESHOLD_MM: Final[float] = 1000.0  # 前方が壁と判定する距離の閾値（mm）
    CORNER_LEFT_THRESHOLD_MM: Final[float] = 1000.0  # 左側がコーナー（壁がない）と判定する距離の閾値（mm）


@dataclass(frozen=True)
class PerceptionConfig:
    """知覚モジュール設定の集約"""
    wall_position: WallPositionPerceptionConfig = WallPositionPerceptionConfig()


# シングルトンインスタンス
perception = PerceptionConfig()
