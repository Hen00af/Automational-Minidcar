#!/usr/bin/env python3
"""
自動運転ミニカーバトル ベースコード
超音波センサーを使用した壁検知・回避走行プログラム

使用方法:
    python3 02_togikai_sample.py
"""

import sys
import time
import RPi.GPIO as GPIO
from togikai_function.motor_control import MotorController
from togikai_function.ultrasonic_sensor import UltrasonicSensor

# GPIO設定
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# センサー・モーターのピン設定
# 注意: 実際のハードウェア構成に合わせて調整してください
ULTRASONIC_TRIGGER = 23  # 超音波センサー トリガーピン
ULTRASONIC_ECHO = 24     # 超音波センサー エコーピン

# 走行パラメータ
MIN_DISTANCE = 20.0      # 最小距離（cm）- この距離以下で停止・回避
NORMAL_SPEED = 50        # 通常走行速度（0-100）
TURN_SPEED = 30          # 旋回時の速度（0-100）
TURN_ANGLE = 45          # 旋回角度（度）

class AutonomousCar:
    """自律走行車クラス"""
    
    def __init__(self):
        """初期化"""
        print("自動運転ミニカーを初期化しています...")
        
        # モーターコントローラーの初期化
        try:
            self.motor = MotorController()
            print("モーターコントローラー: 初期化完了")
        except Exception as e:
            print(f"モーターコントローラー初期化エラー: {e}")
            print("注意: 実機環境でない場合、このエラーは無視できます")
            self.motor = None
        
        # 超音波センサーの初期化
        try:
            self.ultrasonic = UltrasonicSensor(ULTRASONIC_TRIGGER, ULTRASONIC_ECHO)
            print("超音波センサー: 初期化完了")
        except Exception as e:
            print(f"超音波センサー初期化エラー: {e}")
            self.ultrasonic = None
        
        print("初期化完了")
        
    def check_obstacle(self):
        """
        障害物をチェック
        
        Returns:
            float: 距離（cm）。エラー時は-1
        """
        if self.ultrasonic is None:
            # シミュレーション環境の場合、仮の値を返す
            return 100.0
        
        distance = self.ultrasonic.measure_distance()
        return distance
    
    def avoid_obstacle(self):
        """障害物回避動作"""
        print("障害物を検知しました。回避動作を開始します...")
        
        if self.motor is None:
            print("モーターコントローラーが利用できません")
            return
        
        # 1. 停止
        self.motor.stop()
        time.sleep(0.5)
        
        # 2. 左に旋回
        print("左に旋回します...")
        self.motor.set_steering_angle(-TURN_ANGLE)
        self.motor.set_motor_speed(TURN_SPEED)
        time.sleep(1.0)
        
        # 3. 前進
        print("前進します...")
        self.motor.set_steering_angle(0)
        self.motor.set_motor_speed(NORMAL_SPEED)
        time.sleep(1.5)
        
        # 4. 右に旋回して元の方向に戻る
        print("右に旋回して元の方向に戻ります...")
        self.motor.set_steering_angle(TURN_ANGLE)
        self.motor.set_motor_speed(TURN_SPEED)
        time.sleep(1.0)
        
        # 5. 直進に戻る
        self.motor.set_steering_angle(0)
        print("回避動作完了")
    
    def run(self, duration=60):
        """
        メイン走行ループ
        
        Args:
            duration: 走行時間（秒）
        """
        print(f"\n走行を開始します（制限時間: {duration}秒）")
        print("Ctrl+Cで停止できます\n")
        
        start_time = time.time()
        
        try:
            while time.time() - start_time < duration:
                # 距離を測定
                distance = self.check_obstacle()
                
                if distance > 0:
                    print(f"前方距離: {distance:.1f} cm", end="\r")
                
                # 障害物検知
                if distance > 0 and distance < MIN_DISTANCE:
                    print(f"\n警告: 障害物が近すぎます（{distance:.1f} cm）")
                    self.avoid_obstacle()
                else:
                    # 通常走行
                    if self.motor is not None:
                        self.motor.set_steering_angle(0)  # 直進
                        self.motor.set_motor_speed(NORMAL_SPEED)
                
                time.sleep(0.1)  # 100ms間隔でチェック
                
        except KeyboardInterrupt:
            print("\n\nユーザーによって停止されました")
        except Exception as e:
            print(f"\n\nエラーが発生しました: {e}")
        finally:
            # クリーンアップ
            self.cleanup()
    
    def cleanup(self):
        """リソースのクリーンアップ"""
        print("\nクリーンアップ中...")
        
        if self.motor is not None:
            self.motor.cleanup()
        
        if self.ultrasonic is not None:
            self.ultrasonic.cleanup()
        
        # MotorControllerのcleanupでGPIO.cleanup()も実行されるが、
        # 念のため全体のクリーンアップも実行
        try:
            GPIO.cleanup()
        except:
            pass
        
        print("クリーンアップ完了")

def main():
    """メイン関数"""
    print("=" * 50)
    print("自動運転ミニカーバトル - ベースコード")
    print("=" * 50)
    
    car = AutonomousCar()
    
    # 走行時間を設定（デフォルト: 60秒）
    # 実際のレースでは6分（360秒）が制限時間
    run_duration = 60
    
    if len(sys.argv) > 1:
        try:
            run_duration = int(sys.argv[1])
        except ValueError:
            print("警告: 無効な引数。デフォルト値を使用します")
    
    car.run(duration=run_duration)

if __name__ == "__main__":
    main()

