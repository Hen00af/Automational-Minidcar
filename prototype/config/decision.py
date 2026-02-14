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

    KP: Final[float] = 0.005  # P制御の比例ゲイン（左右バランス誤差用）
    KD: Final[float] = (
        0.001  # D制御の微分ゲイン（デフォルトは0.001。0.0を指定すると無効）
    )
    DIFFERENTIAL_SMOOTHING_FACTOR: Final[float] = 0.0  # 微分値の平滑化係数 [0.0, 1.0]
    BASE_SPEED: Final[float] = 0.35  # 通常走行時の基本速度 [0.0, 1.0]
    HIGH_SPEED: Final[float] = 0.40  # 前方が開けている場合の高速 [0.0, 1.0]
    MAX_STEERING: Final[float] = 1.0  # ステアリングの最大値（絶対値）

    # 前方に障害物がある場合の設定
    FRONT_BLOCKED_SPEED: Final[float] = 0.25  # 前方に障害物がある場合の速度
    FRONT_BLOCKED_STEERING: Final[
        float
    ] = -1.0  # 前方障害物時のデフォルトステアリング（右回避、負の値）

    # コーナー予測減速
    CORNER_APPROACH_SPEED: Final[float] = 0.20  # コーナー接近時の減速目標速度


@dataclass(frozen=True)
class DecisionConfig:
    """判断モジュール設定の集約"""

    corridor: CorridorDecisionConfig = CorridorDecisionConfig()


# シングルトンインスタンス
decision = DecisionConfig()
