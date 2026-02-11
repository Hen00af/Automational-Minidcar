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
    KP: Final[float] = 0.005  # P制御の比例ゲイン
    KD: Final[float] = 0.001  # D制御の微分ゲイン（デフォルトは0.001。0.0を指定すると無効）
    DIFFERENTIAL_SMOOTHING_FACTOR: Final[float] = 0.0  # 微分値の平滑化係数 [0.0, 1.0]
    BASE_SPEED: Final[float] = 0.30  # 通常走行時の基本速度 [0.0, 1.0]
    MAX_STEERING: Final[float] = 1.0  # ステアリングの最大値（絶対値）
    
    # 前方に壁がある場合の設定
    FRONT_BLOCKED_SPEED: Final[float] = 0.30 # 前方に壁がある場合の速度
    FRONT_BLOCKED_STEERING: Final[float] = -1.0  # 前方に壁がある場合のステアリング（右折用、負の値、フル右折）
    
    # 左コーナー時の設定
    CORNER_LEFT_SPEED: Final[float] = 0.30 # 左コーナー時の速度
    CORNER_LEFT_STEERING: Final[float] = 0.8  # 左コーナー時のステアリング（左折用、正の値）

    # カーブ減速の設定
    SPEED_REDUCTION_FACTOR: Final[float] = 0.5  # ステアリング角に応じた減速係数 [0.0, 1.0]。0.0で減速なし、1.0でフル操舵時に速度0

    # ステアリングレートリミッターの設定
    MAX_STEERING_RATE: Final[float] = 15.0  # 1秒あたりのステアリング最大変化量。0.0で無制限


@dataclass(frozen=True)
class DecisionConfig:
    """判断モジュール設定の集約"""
    wall_follow: WallFollowDecisionConfig = WallFollowDecisionConfig()


# シングルトンインスタンス
decision = DecisionConfig()
