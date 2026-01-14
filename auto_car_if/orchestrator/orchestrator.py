# --------------------------------
# orchestrator.py  (run_once / run_loop の骨格：設計レベル)
# --------------------------------
from __future__ import annotations

from typing import Optional

from ..interfaces.protocols import CameraModule, SensorModule, Perception, SensorPerception, Decision, Actuation
from ..domain.actuation import Telemetry
from ..domain.command import Command, DriveMode


class Orchestrator:
    """
    全体をつなぐ役（レベル0単一ループ想定）。
    - 中身（アルゴリズム/ハード）を知らず、I/Fだけで接続する。
    - カメラベースとセンサーベースの両方に対応。
    """
    def __init__(
        self,
        camera: Optional[CameraModule] = None,
        perception: Optional[Perception] = None,
        decision: Optional[Decision] = None,
        actuation: Optional[Actuation] = None,
        *,
        sensor: Optional[SensorModule] = None,
        sensor_perception: Optional[SensorPerception] = None,
    ):
        """
        Initialize Orchestrator with either camera or sensor.
        
        Args:
            camera: Camera module (for camera-based navigation) - can be positional
            perception: Camera-based perception module - can be positional
            decision: Decision module - can be positional
            actuation: Actuation module - can be positional
            sensor: Sensor module (for sensor-based navigation) - keyword only
            sensor_perception: Sensor-based perception module - keyword only
        
        Note: For backward compatibility, the old signature (camera, perception, decision, actuation)
        as positional arguments is supported. For sensor-based mode, use keyword arguments.
        
        Examples:
            # Camera-based (legacy, positional args)
            Orchestrator(camera, perception, decision, actuation)
            
            # Sensor-based (new, keyword args)
            Orchestrator(decision=decision, actuation=actuation, sensor=sensor, sensor_perception=sensor_perception)
        """
        # 位置引数で4つ渡された場合（後方互換性）
        if camera is not None and perception is not None and decision is not None and actuation is not None:
            if sensor is not None or sensor_perception is not None:
                raise ValueError("Cannot mix camera-based (positional) and sensor-based (keyword) arguments")
            self.camera = camera
            self.sensor = None
            self.perception = perception
            self.sensor_perception = None
            self.decision = decision
            self.actuation = actuation
            self._is_sensor_mode = False
            return
        
        # センサーベースの場合
        if sensor is not None:
            if camera is not None:
                raise ValueError("Cannot use both camera and sensor at the same time")
            if sensor_perception is None:
                raise ValueError("SensorPerception module is required when using sensor")
            if decision is None:
                raise ValueError("Decision module is required")
            if actuation is None:
                raise ValueError("Actuation module is required")
            self.camera = None
            self.sensor = sensor
            self.perception = None
            self.sensor_perception = sensor_perception
            self.decision = decision
            self.actuation = actuation
            self._is_sensor_mode = True
            return
        
        # カメラベースの場合（キーワード引数）
        if camera is not None:
            if sensor is not None:
                raise ValueError("Cannot use both camera and sensor at the same time")
            if perception is None:
                raise ValueError("Perception module is required when using camera")
            if decision is None:
                raise ValueError("Decision module is required")
            if actuation is None:
                raise ValueError("Actuation module is required")
            self.camera = camera
            self.sensor = None
            self.perception = perception
            self.sensor_perception = None
            self.decision = decision
            self.actuation = actuation
            self._is_sensor_mode = False
            return
        
        # どちらも指定されていない
        raise ValueError("Either camera (positional or keyword) or sensor (keyword) must be provided")

    def run_once(self, frame_or_reading) -> Telemetry:
        """
        1フレーム分の処理（例外処理や安全停止ポリシーは必要に応じて追加）。
        カメラベースとセンサーベースの両方に対応。
        """
        if self._is_sensor_mode:
            reading = frame_or_reading
            print(f"[Orchestrator] reading_id={getattr(reading, 'reading_id', '?')}, t_capture_sec={getattr(reading, 't_capture_sec', '?')}")
            features = self.sensor_perception.process_sensor(reading)
        else:
            frame = frame_or_reading
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
        カメラベースとセンサーベースの両方に対応。
        """
        if self._is_sensor_mode:
            for reading in self.sensor.readings():
                _ = self.run_once(reading)
        else:
            for frame in self.camera.frames():
                _ = self.run_once(frame)

    def emergency_stop(self, reason: str = "emergency") -> Telemetry:
        """
        上位から明示停止できる入口（設計上の口）。
        """
        return self.actuation.stop(reason)

