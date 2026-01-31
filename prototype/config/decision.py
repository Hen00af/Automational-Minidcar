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
    KP: Final[float] = 0.01  # P制御の比例ゲイン
    KD: Final[float] = 0.001  # D制御の微分ゲイン（デフォルトは0.001。0.0を指定すると無効）
    DIFFERENTIAL_SMOOTHING_FACTOR: Final[float] = 0.0  # 微分値の平滑化係数 [0.0, 1.0]
    BASE_SPEED: Final[float] = 0.28  # 通常走行時の基本速度 [0.0, 1.0]
    MAX_STEERING: Final[float] = 1.0  # ステアリングの最大値（絶対値）
    
    # 前方に壁がある場合の設定
    FRONT_BLOCKED_SPEED: Final[float] = 0.25  # 前方に壁がある場合の速度
    FRONT_STEER_GAIN: Final[float] = 0.0005  # 前方壁回避の比例ゲイン Kf (steer = clamp(-Kf*(F_th - F), -1, 0))
    FRONT_THRESHOLD_MM: Final[float] = 2000.0  # 前方壁回避が始まる距離閾値 (mm)

    # 左コーナー時の設定
    CORNER_LEFT_SPEED: Final[float] = 0.25  # 左コーナー時の速度
    CORNER_LEFT_STEER_GAIN: Final[float] = 0.0004  # 左コーナーの比例ゲイン Kc (steer = clamp(Kc*(LF - LF_th), 0, 1))
    CORNER_LEFT_THRESHOLD_MM: Final[float] = 2000.0  # 左コーナー判定の距離閾値 (mm)


@dataclass(frozen=True)
class DecisionConfig:
    """判断モジュール設定の集約"""
    wall_follow: WallFollowDecisionConfig = WallFollowDecisionConfig()


# シングルトンインスタンス
decision = DecisionConfig()
