#!/usr/bin/env python3
"""
実機でオーケストレーターを実行するスクリプト
"""
from act.orchestrator import Orchestrator
from act.sensors import TOFSensor
from act.perception import WallPositionPerception
from act.decision import WallFollowDecision
from act.actuation import PWMActuation
from act.domain.actuation import ActuationCalibration
import time
from act.config import timing


def main():
    print("[REAL MODE] Initializing components...")
    
    # 実機実装を使用
    sensor = TOFSensor()
    perception = WallPositionPerception(target_distance_mm=200.0)
    decision = WallFollowDecision(kp=0.03, base_speed=0.5)  # 純粋なP制御（kdパラメータは削除）
    actuation = PWMActuation()
    
    # キャリブレーションを設定
    calib = ActuationCalibration(
        steer_center_us=1500,  # 中央
        steer_left_us=1300,    # 左（steer=+1.0）
        steer_right_us=1700,   # 右（steer=-1.0）
        throttle_stop_us=1500,  # 停止
        throttle_max_us=1600   # 最大（throttle=+1.0）
    )
    actuation.configure(calib)
    
    # ESC初期化の完了を待つ（念のため）
    print(f"[REAL MODE] Waiting {timing.esc_init.NEUTRAL_WAIT}s for ESC initialization...")
    time.sleep(timing.esc_init.NEUTRAL_WAIT)
    
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
