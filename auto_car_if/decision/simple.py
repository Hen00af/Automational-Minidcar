"""Simple P-controller based decision module."""
from __future__ import annotations

from ..domain.features import Features, PerceptionStatus
from ..domain.command import Command, DriveMode


class SimpleDecision:
    def __init__(
        self,
        k_steer: float = 0.8,
        max_abs_steer: float = 1.0,
        max_throttle: float = 0.5,
        quality_thresh: float = 0.2,
    ) -> None:
        self.k_steer = k_steer
        self.max_abs_steer = max_abs_steer
        self.max_throttle = max_throttle
        self.quality_thresh = quality_thresh

    def decide(self, features: Features) -> Command:
        if features.status != PerceptionStatus.OK or features.quality < self.quality_thresh:
            return Command(
                frame_id=features.frame_id,
                t_capture_sec=features.t_capture_sec,
                steer=0.0,
                throttle=0.0,
                mode=DriveMode.STOP,
                reason="low_quality",
            )

        steer = -self.k_steer * features.lateral_bias
        steer = max(-self.max_abs_steer, min(self.max_abs_steer, steer))
        throttle = max(0.0, min(self.max_throttle, self.max_throttle))

        return Command(
            frame_id=features.frame_id,
            t_capture_sec=features.t_capture_sec,
            steer=steer,
            throttle=throttle,
            mode=DriveMode.RUN,
            reason="tracking",
        )
