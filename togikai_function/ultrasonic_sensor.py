"""
超音波センサー制御用モジュール
HC-SR04などの超音波センサーを使用した距離測定関数
"""

import RPi.GPIO as GPIO
import time

class UltrasonicSensor:
    """超音波センサークラス"""
    
    def __init__(self, trigger_pin, echo_pin):
        """
        初期化
        
        Args:
            trigger_pin: トリガーピン番号
            echo_pin: エコーピン番号
        """
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        
        # GPIO設定
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.trigger_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)
        
        # 初期化
        GPIO.output(self.trigger_pin, False)
        time.sleep(0.1)
        
    def measure_distance(self):
        """
        距離を測定（cm単位）
        
        Returns:
            float: 距離（cm）。エラー時は-1を返す
        """
        try:
            # トリガー信号を送信
            GPIO.output(self.trigger_pin, True)
            time.sleep(0.00001)  # 10マイクロ秒
            GPIO.output(self.trigger_pin, False)
            
            # エコー信号の受信を待つ
            timeout = time.time() + 0.03  # 30msのタイムアウト
            while GPIO.input(self.echo_pin) == 0:
                if time.time() > timeout:
                    return -1
                pulse_start = time.time()
            
            pulse_start = time.time()
            timeout = time.time() + 0.03
            while GPIO.input(self.echo_pin) == 1:
                if time.time() > timeout:
                    return -1
                pulse_end = time.time()
            
            # 距離を計算（音速: 34300 cm/s）
            pulse_duration = pulse_end - pulse_start
            distance = (pulse_duration * 34300) / 2
            
            return distance
            
        except Exception as e:
            print(f"距離測定エラー: {e}")
            return -1
    
    def cleanup(self):
        """GPIOのクリーンアップ"""
        GPIO.cleanup([self.trigger_pin, self.echo_pin])

