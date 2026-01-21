# --------------------------------
# config/decision.py
# 判断モジュール関連の設定定数
# --------------------------------
from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class WallFollowDecisionConfig:
    """壁沿い走行判断モジュール設定"""
    KP: Final[float] = 0.03  # P制御の比例ゲイン
    BASE_SPEED: Final[float] = 0.5  # 通常走行時の基本速度 [0.0, 1.0]
    MAX_STEERING: Final[float] = 1.0  # ステアリングの最大値（絶対値）
    
    # 前方に壁がある場合の設定
    FRONT_BLOCKED_SPEED: Final[float] = 0.0  # 前方に壁がある場合の速度
    FRONT_BLOCKED_STEERING: Final[float] = -0.5  # 前方に壁がある場合のステアリング（右折用、負の値）
    
    # 左コーナー時の設定
    CORNER_LEFT_SPEED: Final[float] = 0.3  # 左コーナー時の速度
    CORNER_LEFT_STEERING: Final[float] = 0.8  # 左コーナー時のステアリング（左折用、正の値）


@dataclass(frozen=True)
class DecisionConfig:
    """判断モジュール設定の集約"""
    wall_follow: WallFollowDecisionConfig = WallFollowDecisionConfig()


# シングルトンインスタンス
decision = DecisionConfig()
