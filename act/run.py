#!/usr/bin/env python3
"""
実機でオーケストレーターを実行するスクリプト
"""
from act.orchestrator import Orchestrator
from act.sensors import TOFSensor
from act.perception import WallPositionPerception
from act.decision import WallFollowDecision
from act.actuation import PWMActuation


def main():
    print("[REAL MODE] Initializing components...")
    
    # 実機実装を使用
    sensor = TOFSensor()
    perception = WallPositionPerception(target_distance_mm=200.0)
    decision = WallFollowDecision(kp=0.03, base_speed=0.5)  # 純粋なP制御（kdパラメータは削除）
    actuation = PWMActuation()
    
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
