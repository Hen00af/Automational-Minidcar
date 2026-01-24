# --------------------------------
# config/orchestrator.py
# オーケストレーター関連の設定定数
# --------------------------------
from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class OrchestratorConfig:
    """オーケストレーター設定"""
    # ループ間隔（秒）。デフォルトは0.1秒（10Hz）
    # 
    # 制約:
    # - 理論的最小値: 0.02秒（20ms、50Hz）- PWM周期（PCA9685は50Hz）に合わせる
    # - 実用的最小値: 0.05秒（50ms）- VL53L0Xセンサー3つの順次読み取り（各20-30ms）+ I2C通信オーバーヘッド
    # - 推奨範囲: 0.05-0.1秒（50-100ms）- センサー応答と処理時間を考慮
    # - 現在の設定: 0.1秒（100ms）- 安全マージンあり
    LOOP_INTERVAL_SEC: Final[float] = 0.1
    LOG_INTERVAL_SEC: Final[float] = 1.0  # 詳細ログ出力間隔（秒）。デフォルトは1.0秒


# シングルトンインスタンス
orchestrator = OrchestratorConfig()
