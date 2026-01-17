# interfaces パッケージ
# 各モジュール間のインターフェース（プロトコル）を定義

from .protocols import (
    CameraModule,
    DistanceSensorModule,
    Perception,
    Decision,
    Actuation,
)

__all__ = [
    "CameraModule",
    "DistanceSensorModule",
    "Perception",
    "Decision",
    "Actuation",
]
