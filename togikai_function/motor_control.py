"""
モーター制御用モジュール
GPIOから直接ESCとサーボを制御（PWM分岐ケーブル経由）
周期17ms(60Hz)のPWMパルスを生成
"""

import time
import RPi.GPIO as GPIO

# PWM周期: 17ms = 60Hz（サーボモーター標準）
PWM_FREQUENCY = 60  # Hz
PWM_PERIOD = 1.0 / PWM_FREQUENCY  # 17ms

# サーボモーターのパルス幅範囲（一般的な値）
SERVO_MIN_PULSE = 0.5   # ms（最小角度）
SERVO_MAX_PULSE = 2.5   # ms（最大角度）
SERVO_CENTER_PULSE = 1.5  # ms（中央位置）

# ESC（電子速度制御）のパルス幅範囲
ESC_MIN_PULSE = 1.0   # ms（停止/最小速度）
ESC_MAX_PULSE = 2.0   # ms（最大速度）
ESC_CENTER_PULSE = 1.5  # ms（ニュートラル）

class MotorController:
    """モーター制御クラス（GPIO直接制御）"""
    
    def __init__(self, steering_pin=18, motor_pin=19):
        """
        初期化
        
        Args:
            steering_pin: ステアリング用サーボのGPIOピン番号（デフォルト: 18）
            motor_pin: 駆動モーター（ESC）のGPIOピン番号（デフォルト: 19）
        """
        self.steering_pin = steering_pin
        self.motor_pin = motor_pin
        
        # GPIO設定
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # PWM初期化（周期17ms = 60Hz）
        GPIO.setup(self.steering_pin, GPIO.OUT)
        GPIO.setup(self.motor_pin, GPIO.OUT)
        
        self.steering_pwm = GPIO.PWM(self.steering_pin, PWM_FREQUENCY)
        self.motor_pwm = GPIO.PWM(self.motor_pin, PWM_FREQUENCY)
        
        # PWM開始（デューティ比0%で開始）
        self.steering_pwm.start(0)
        self.motor_pwm.start(0)
        
        # 初期化時にニュートラル位置に設定
        self.set_steering_angle(0)
        self.set_motor_speed(0)
        
    def _pulse_width_to_duty_cycle(self, pulse_width_ms):
        """
        パルス幅（ms）をデューティ比（%）に変換
        
        Args:
            pulse_width_ms: パルス幅（ミリ秒）
            
        Returns:
            float: デューティ比（%）
        """
        duty_cycle = (pulse_width_ms / (PWM_PERIOD * 1000)) * 100
        return max(0, min(100, duty_cycle))
    
    def set_steering_angle(self, angle):
        """
        ステアリング角度を設定
        
        Args:
            angle: 角度（-90度から90度、0度が中央）
        """
        # 角度を-90〜90度の範囲に制限
        angle = max(-90, min(90, angle))
        
        # 角度をパルス幅に変換
        # -90度: SERVO_MIN_PULSE, 0度: SERVO_CENTER_PULSE, 90度: SERVO_MAX_PULSE
        if angle == 0:
            pulse_width = SERVO_CENTER_PULSE
        elif angle > 0:
            # 右に曲がる（0度から90度）
            ratio = angle / 90.0
            pulse_width = SERVO_CENTER_PULSE + ratio * (SERVO_MAX_PULSE - SERVO_CENTER_PULSE)
        else:
            # 左に曲がる（-90度から0度）
            ratio = abs(angle) / 90.0
            pulse_width = SERVO_CENTER_PULSE - ratio * (SERVO_CENTER_PULSE - SERVO_MIN_PULSE)
        
        # デューティ比に変換してPWM出力
        duty_cycle = self._pulse_width_to_duty_cycle(pulse_width)
        self.steering_pwm.ChangeDutyCycle(duty_cycle)
        
    def set_motor_speed(self, speed):
        """
        モーター速度を設定（ESC制御）
        
        Args:
            speed: 速度（-100から100、0が停止/ニュートラル、正の値が前進、負の値が後進）
        """
        # 速度を-100〜100の範囲に制限
        speed = max(-100, min(100, speed))
        
        # 速度をパルス幅に変換
        # -100: ESC_MIN_PULSE, 0: ESC_CENTER_PULSE, 100: ESC_MAX_PULSE
        if speed == 0:
            pulse_width = ESC_CENTER_PULSE  # ニュートラル
        elif speed > 0:
            # 前進
            ratio = speed / 100.0
            pulse_width = ESC_CENTER_PULSE + ratio * (ESC_MAX_PULSE - ESC_CENTER_PULSE)
        else:
            # 後進
            ratio = abs(speed) / 100.0
            pulse_width = ESC_CENTER_PULSE - ratio * (ESC_CENTER_PULSE - ESC_MIN_PULSE)
        
        # デューティ比に変換してPWM出力
        duty_cycle = self._pulse_width_to_duty_cycle(pulse_width)
        self.motor_pwm.ChangeDutyCycle(duty_cycle)
        
    def stop(self):
        """モーターを停止（ニュートラル位置に設定）"""
        self.set_motor_speed(0)
        self.set_steering_angle(0)
        
    def cleanup(self):
        """リソースのクリーンアップ"""
        self.stop()
        time.sleep(0.1)  # PWM停止前に少し待機
        self.steering_pwm.stop()
        self.motor_pwm.stop()
        GPIO.cleanup([self.steering_pin, self.motor_pin])
