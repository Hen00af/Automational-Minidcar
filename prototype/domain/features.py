# --------------------------------
# domain/features.py
# 回廊走行用の特徴量型定義
# --------------------------------
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class WallFeatures:
    """
    知覚モジュールが抽出した特徴量（回廊中央走行用）
    """

    left_right_error: float    # 左右バランス誤差（正=右寄り→左に寄る、負=左寄り→右に寄る）
    is_front_blocked: bool     # 前方に障害物があるか（回避判断用）
    front_distance_mm: float   # 前方距離（速度制御用）
    left_front_mm: float       # 左斜め前距離（回避方向判断用）
    right_front_mm: float      # 右斜め前距離（回避方向判断用）
