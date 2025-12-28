from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class VehicleState:
    """
    将来拡張用の状態（雛形）。
    例: 変化率制限、スムージング、PID、見失い継続の判断などに使える。
    """
    t_state_sec: float

    prev_steer: Optional[float] = None      # [-1, +1]
    prev_throttle: Optional[float] = None   # [0, +1]
    dt_sec: Optional[float] = None

    lost_count: Optional[int] = None

