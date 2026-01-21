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
    LOOP_INTERVAL_SEC: Final[float] = 0.1  # ループ間隔（秒）。デフォルトは0.1秒（10Hz）
    LOG_INTERVAL_SEC: Final[float] = 1.0  # 詳細ログ出力間隔（秒）。デフォルトは1.0秒


# シングルトンインスタンス
orchestrator = OrchestratorConfig()
