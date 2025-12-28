#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
orchestrator_skeleton.py の動作テスト（モック環境）
"""

from auto_car_if.main import Orchestrator
from auto_car_if.domain.frame import Frame, ImageBuffer, ColorSpace, PixelFormat
from auto_car_if.domain.features import Features, PerceptionStatus
from auto_car_if.domain.command import Command, DriveMode
from auto_car_if.domain.actuation import Telemetry, ActuationStatus


# ダミー画像バッファクラス
class DummyImageBuffer:
    """ImageBufferプロトコルのダミー実装"""
    def __init__(self, w=640, h=480, c=3):
        self._width = w
        self._height = h
        self._channels = c
    
    @property
    def width(self) -> int:
        return self._width
    
    @property
    def height(self) -> int:
        return self._height
    
    @property
    def channels(self) -> int:
        return self._channels
    
    @property
    def pixel_format(self) -> PixelFormat:
        return PixelFormat.UINT8
    
    @property
    def color_space(self) -> ColorSpace:
        return ColorSpace.RGB
    
    def as_bytes(self) -> bytes:
        return b'\x00' * (self._width * self._height * self._channels)


# ダミー実装クラス
class DummyCamera:
    """カメラモジュールのダミー実装"""
    def __init__(self, num_frames=3):
        self.num_frames = num_frames
    
    def frames(self):
        """フレームを生成（ジェネレータ）"""
        for i in range(self.num_frames):
            print(f"📷 カメラ: フレーム {i+1} をキャプチャ")
            yield Frame(
                frame_id=i,
                t_capture_sec=i * 0.1,
                image=DummyImageBuffer()
            )


class DummyPerception:
    """認識モジュールのダミー実装"""
    def process(self, frame: Frame) -> Features:
        print(f"🔍 認識: フレーム {frame.frame_id} を処理中")
        # ダミーの特徴量を返す
        return Features(
            frame_id=frame.frame_id,
            t_capture_sec=frame.t_capture_sec,
            lateral_bias=0.1,  # 少し左寄り
            quality=0.8,
            status=PerceptionStatus.OK
        )


class DummyDecision:
    """判断モジュールのダミー実装"""
    def decide(self, features: Features) -> Command:
        print(f"🤔 判断: 特徴量から指令を生成 (lateral_bias={features.lateral_bias:.2f})")
        # ダミーの指令を返す
        return Command(
            frame_id=features.frame_id,
            t_capture_sec=features.t_capture_sec,
            mode=DriveMode.RUN,
            throttle=0.5,
            steer=features.lateral_bias,  # lateral_biasをそのまま使用
            reason="normal_operation"
        )


class DummyActuation:
    """制御モジュールのダミー実装"""
    def apply(self, command: Command) -> Telemetry:
        print(f"⚙️  制御: 指令を適用 (スロットル={command.throttle:.2f}, ステアリング={command.steer:.2f})")
        # ダミーのテレメトリを返す
        return Telemetry(
            frame_id=command.frame_id,
            t_capture_sec=command.t_capture_sec,
            status=ActuationStatus.OK,
            applied_throttle=command.throttle,
            applied_steer=command.steer,
            steer_pwm_us=1500,
        )
    
    def stop(self, reason: str) -> Telemetry:
        print(f"🛑 緊急停止: {reason}")
        return Telemetry(
            frame_id=0,
            t_capture_sec=0.0,
            status=ActuationStatus.STOPPED,
            applied_throttle=0.0,
            applied_steer=0.0,
        )


def main():
    print("=" * 60)
    print("🚗 Orchestrator テスト実行")
    print("=" * 60)
    
    # ダミーモジュールを作成
    camera = DummyCamera(num_frames=3)
    perception = DummyPerception()
    decision = DummyDecision()
    actuation = DummyActuation()
    
    # Orchestratorを初期化
    orchestrator = Orchestrator(
        camera=camera,
        perception=perception,
        decision=decision,
        actuation=actuation
    )
    
    print("\n--- run_loop() テスト ---\n")
    orchestrator.run_loop()
    
    print("\n--- emergency_stop() テスト ---\n")
    telemetry = orchestrator.emergency_stop("テスト停止")
    print(f"結果: {telemetry}")
    
    print("\n" + "=" * 60)
    print("✅ テスト完了")
    print("=" * 60)


if __name__ == "__main__":
    main()
