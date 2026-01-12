from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

class DriveMode(str, Enum):
    RUN = "RUN"
    SLOW = "SLOW"
    STOP = "STOP"

@dataclass(frozen=True)
class Command:
    """
    Decision -> Actuation 出力。

    Contract:
    - steer: [-1.0, +1.0]
        + : 左へ切る
        - : 右へ切る
    - throttle: [-1.0, +1.0]
        -1.0: 後退最大
        0.0: 停止
        +1.0: 前進最大
    - STOP の場合、throttle == 0.0 を保証する（安全契約）
    """
    frame_id: int
    t_capture_sec: float

    steer: float          # [-1, +1]
    throttle: float       # [-1, +1]
    mode: DriveMode

    reason: Optional[str] = None

