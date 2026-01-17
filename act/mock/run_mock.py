#!/usr/bin/env python3
"""
モック実装でオーケストレーターを実行するスクリプト
"""
from act.orchestrator import Orchestrator
from act.mock import MockTOFSensor
from act.perception import WallPositionPerception
from act.decision import WallFollowDecision
from act.mock import MockActuation
from act.domain.actuation import ActuationCalibration


def main():
    print("[MOCK MODE] Initializing components...")
    
    # モック実装を使用（動的モード：時間経過で値が変化）
    sensor = MockTOFSensor(
        left_distance=200,  # 目標距離に設定
        front_distance=500,
        right_distance=300,
        use_random=False,
        use_dynamic=True,  # 時間経過で値が変化する動的モックを有効化
        verbose=False  # 詳細ログを無効化（orchestratorのテーブルログのみ表示）
    )
    perception = WallPositionPerception(target_distance_mm=200.0)
    decision = WallFollowDecision(base_speed=0.5)  # kpはデフォルト値0.03を使用（純粋なP制御）
    actuation = MockActuation(verbose=False)  # 詳細ログを無効化（orchestratorのテーブルログのみ表示）
    
    # キャリブレーションを設定（const.pyの値を使用）
    calib = ActuationCalibration(
        steer_center_us=1500,  # 中央
        steer_left_us=1300,    # 左（steer=+1.0）
        steer_right_us=1700,   # 右（steer=-1.0）
        throttle_stop_us=1500,  # 停止
        throttle_max_us=1600   # 最大（throttle=+1.0）
    )
    actuation.configure(calib)
    
    # オーケストレーターを作成
    orchestrator = Orchestrator(sensor, perception, decision, actuation)
    
    print("[MOCK MODE] Starting loop (Ctrl+C to stop)...")
    print("[MOCK MODE] Loop interval: 0.1s (10Hz), Log interval: 1.0s")
    print("[MOCK MODE] Dynamic mode enabled: sensor values will change over time")
    try:
        orchestrator.run_loop(loop_interval_sec=0.1, log_interval_sec=1.0)
    except KeyboardInterrupt:
        print("\n[MOCK MODE] Stopped by user")
    finally:
        actuation.close()


if __name__ == "__main__":
    main()
