from __future__ import annotations

from typing import Iterator, Protocol

from ..domain.frame import Frame
from ..domain.sensor import SensorReading
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

class SensorModule(Protocol):
    """
    Sensor module external I/F:
    - 距離センサー（超音波、赤外線など）から測定値を提供する責務
    """
    def readings(self) -> Iterator[SensorReading]:
        ...

class Perception(Protocol):
    """Perception external I/F: Frame -> Features"""
    def process(self, frame: Frame) -> Features:
        ...

class SensorPerception(Protocol):
    """
    Sensor-based Perception external I/F: SensorReading -> Features
    
    Note: 将来的にカメラからセンサーに置き換える場合に使用。
    Featuresのsignalsフィールドに距離情報（distance_cm等）を格納する。
    """
    def process_sensor(self, reading: SensorReading) -> Features:
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
