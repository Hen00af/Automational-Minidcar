# --------------------------------
# interfaces/protocols.py  (Cのprototype相当)
# --------------------------------
from __future__ import annotations

from typing import Iterator, Protocol

from ..domain.distance import DistanceData
from ..domain.features import WallFeatures
from ..domain.command import Command
from ..domain.actuation import ActuationCalibration, Telemetry


class CameraModule(Protocol):
    """
    Camera module external I/F:
    - 最新フレームを提供する責務（RGB固定などの正規化はここで行う方針）
    """
    def frames(self) -> Iterator:
        ...


class DistanceSensorModule(Protocol):
    """
    Distance sensor module external I/F:
    - 3方向の距離を計測して返す責務
    """
    def read(self) -> DistanceData:
        """3方向の距離を計測して返す"""
        ...

    def poll(self) -> tuple[bool, DistanceData]:
        """data-readyなセンサーを読み出し、更新有無とデータを返す"""
        ...

    def start_continuous(self) -> None:
        """連続計測モードを開始"""
        ...

    def stop_continuous(self) -> None:
        """連続計測モードを停止"""
        ...


class Perception(Protocol):
    """
    Perception external I/F:
    - 距離センサー版: DistanceData -> WallFeatures
    """
    def analyze(self, data: DistanceData) -> WallFeatures:
        """距離センサー版: DistanceData -> WallFeatures"""
        ...


class Decision(Protocol):
    """
    Decision external I/F (第1イテレーション):
    - カメラ版: Features -> Command
    - 距離センサー版: WallFeatures -> Command
    """
    def decide(self, features: WallFeatures) -> Command:
        """状況に基づいてハンドル・アクセルを決定する"""
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
