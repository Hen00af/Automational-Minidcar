# --------------------------------
# domain/features.py
# 壁沿い走行用の特徴量型定義
# --------------------------------
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class WallFeatures:
    """
    知覚モジュールが抽出した特徴量（壁沿い走行用）
    """

    error_from_target: float  # 目標距離とのズレ（正なら離れすぎ、負なら近すぎ）
    is_front_blocked: bool  # 前方に壁があるか（右折・停止判断用）
    is_left_wall: bool  # 左に壁があるか（左折判断用）
