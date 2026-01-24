#!/usr/bin/env python3
"""
実機でオーケストレーターを実行するスクリプト
"""
from prototype.orchestrator import Orchestrator
from prototype.sensors import TOFSensor
from prototype.perception import WallPositionPerception
from prototype.decision import WallFollowDecision
from prototype.actuation import PWMActuation
from prototype.domain.actuation import ActuationCalibration
from prototype.config import hardware


def main():
    print("[REAL MODE] Initializing components...")
    
    # 実機実装を使用
    sensor = TOFSensor()
    perception = WallPositionPerception()  # 設定ファイルからデフォルト値を読み込む
    decision = WallFollowDecision()  # 設定ファイルからデフォルト値を読み込む
    actuation = PWMActuation()
    
    # キャリブレーションを設定（設定ファイルから値を読み込む）
    calib = ActuationCalibration(
        steer_center_us=hardware.servo.US_CENTER,  # 中央
        steer_left_us=hardware.servo.US_LEFT,    # 左（steer=+1.0）
        steer_right_us=hardware.servo.US_RIGHT,   # 右（steer=-1.0）
        throttle_stop_us=hardware.esc.US_NEUTRAL,  # 停止
        throttle_max_us=hardware.esc.US_FORWARD_SLOW   # 最大（throttle=+1.0）
    )
    actuation.configure(calib)
    
    # オーケストレーターを作成
    orchestrator = Orchestrator(sensor, perception, decision, actuation)
    
    print("[REAL MODE] Starting loop (Ctrl+C to stop)...")
    try:
        orchestrator.run_loop()
    except KeyboardInterrupt:
        print("\n[REAL MODE] Stopped by user")
    finally:
        actuation.close()


if __name__ == "__main__":
    main()
