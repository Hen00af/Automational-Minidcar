# --------------------------------
# orchestrator.py  (run_once / run_loop の骨格：設計レベル)
# --------------------------------
from __future__ import annotations

from typing import Optional

from ..interfaces.protocols import CameraModule, Perception, Decision, Actuation
from ..domain.actuation import Telemetry
from ..domain.command import Command, DriveMode


class Orchestrator:
    """
    全体をつなぐ役（レベル0単一ループ想定）。
    - 中身（アルゴリズム/ハード）を知らず、I/Fだけで接続する。
    """
    def __init__(self, camera: CameraModule, perception: Perception, decision: Decision, actuation: Actuation):
        self.camera = camera
        self.perception = perception
        self.decision = decision
        self.actuation = actuation

    def run_once(self, frame) -> Telemetry:
        """
        1フレーム分の処理（例外処理や安全停止ポリシーは必要に応じて追加）。
        """
        print(f"[Orchestrator] frame_id={getattr(frame, 'frame_id', '?')}, t_capture_sec={getattr(frame, 't_capture_sec', '?')}")
        features = self.perception.process(frame)
        print(f"[Orchestrator] features: {features}")
        command = self.decision.decide(features)
        print(f"[Orchestrator] command: {command}")
        telemetry = self.actuation.apply(command)
        print(f"[Orchestrator] telemetry: {telemetry}\n")
        return telemetry

    def run_loop(self) -> None:
        """
        連続実行（第1イテレーションは単純に繰り返すだけ）。
        最新優先の高度化（古いフレーム破棄等）は次イテレーションで扱う。
        """
        for frame in self.camera.frames():
            _ = self.run_once(frame)

    def emergency_stop(self, reason: str = "emergency") -> Telemetry:
        """
        上位から明示停止できる入口（設計上の口）。
        """
        return self.actuation.stop(reason)

