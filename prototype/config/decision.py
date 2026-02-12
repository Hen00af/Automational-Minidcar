# --------------------------------
# config/decision.py
# 判断モジュール関連の設定定数
# --------------------------------
from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class CorridorDecisionConfig:
    """回廊走行判断モジュール設定"""
    KP: Final[float] = 0.002  # P制御の比例ゲイン（左右バランス誤差用）。飽和を防ぐため低めに設定
    KD: Final[float] = 0.008  # D制御の微分ゲイン。直進性確保のため強めに設定
    DIFFERENTIAL_SMOOTHING_FACTOR: Final[float] = 0.3  # 微分値の平滑化係数 [0.0, 1.0]。D項の安定化
    MAX_D_TERM: Final[float] = 0.5  # D制御項の最大値（絶対値）。D項の暴走を防止
    BASE_SPEED: Final[float] = 0.30  # 通常走行時の基本速度 [0.0, 1.0]
    HIGH_SPEED: Final[float] = 0.50  # 前方が開けている場合の高速 [0.0, 1.0]
    MAX_STEERING: Final[float] = 0.7  # ステアリングの最大値（絶対値）。急旋回を抑制

    # 前方に障害物がある場合の設定
    FRONT_BLOCKED_SPEED: Final[float] = 0.25  # 前方に障害物がある場合の速度
    FRONT_BLOCKED_STEERING: Final[float] = -1.0  # 前方障害物時のデフォルトステアリング（右回避、負の値）


@dataclass(frozen=True)
class DecisionConfig:
    """判断モジュール設定の集約"""
    corridor: CorridorDecisionConfig = CorridorDecisionConfig()


# シングルトンインスタンス
decision = DecisionConfig()
