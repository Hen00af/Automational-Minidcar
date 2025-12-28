from __future__ import annotations

from typing import Iterator, Protocol

from ..domain.frame import Frame
from ..domain.features import Features
from ..domain.command import Command
from ..domain.actuation import ActuationCalibration, Telemetry

class CameraModule(Protocol):
    """
    Camera module external I/F:
    - 最新フレームを提供する責務（RGB固定などの正規化はここで行う方針）
    """
    def frames(self) -> Iterator[Frame]:
        ...

class Perception(Protocol):
    """Perception external I/F: Frame -> Features"""
    def process(self, frame: Frame) -> Features:
        ...

class Decision(Protocol):
    """Decision external I/F (第1イテレーション): Features -> Command"""
    def decide(self, features: Features) -> Command:
        ...

class Actuation(Protocol):
    """Actuation external I/F: Command -> Telemetry"""
    def configure(self, calib: ActuationCalibration) -> None:
        ...

    def apply(self, command: Command) -> Telemetry:
        ...

    def stop(self, reason: str) -> Telemetry:
        ...

    def close(self) -> None:
        ...
