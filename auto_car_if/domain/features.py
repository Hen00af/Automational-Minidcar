from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Optional

class PerceptionStatus(str, Enum):
    OK = "OK"
    INSUFFICIENT_SIGNAL = "INSUFFICIENT_SIGNAL"
    INVALID_INPUT = "INVALID_INPUT"

@dataclass(frozen=True)
class Features:
    """
    Perception -> Decision 出力。

    Contract:
    - lateral_bias: [-1.0, +1.0]
        + : 左へ寄りたい（右側の圧迫が強い等）
        - : 右へ寄りたい（左側の圧迫が強い等）
    - quality: [0.0, 1.0]
        推定の信頼度（0は信用しない、1は高信頼）
    """
    frame_id: int
    t_capture_sec: float

    lateral_bias: float   # [-1, +1]
    quality: float        # [0, 1]

    # 任意：追加の数値観測（拡張用）
    signals: Optional[Mapping[str, float]] = None

    # 任意：デバッグ用（Decisionは参照しない方針）
    debug: Optional[Mapping[str, Any]] = None

    status: PerceptionStatus = PerceptionStatus.OK

