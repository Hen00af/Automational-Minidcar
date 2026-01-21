 # --------------------------------
 # actuation/pwm.py
 # PCA9685を使用したPWM制御実装（実機用）
 # --------------------------------
 from __future__ import annotations
 
-import sys
+import logging
 import os
+import sys
 from typing import Optional
 
 # ハードウェアモジュールの自動インポート
 # kudou_test/hardware_import.py のロジックを参考
 def _is_raspberry_pi() -> bool:
     """Raspberry Pi環境かどうかを判定"""
     try:
         with open('/proc/cpuinfo', 'r') as f:
             cpuinfo = f.read()
             return 'Raspberry Pi' in cpuinfo or 'BCM' in cpuinfo
     except (FileNotFoundError, PermissionError):
         pass
     
     return False  # Docker環境では常にFalse
 
 # ハードウェアモジュールのインポート
 _is_non_raspberry = not _is_raspberry_pi()
 
 if _is_non_raspberry:
     # 非Raspberry Pi環境ではkudou_testからハードウェアモジュールをインポート
     try:
         # kudou_testディレクトリをパスに追加
         kudou_test_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'kudou_test')
         if kudou_test_path not in sys.path:
             sys.path.insert(0, kudou_test_path)
@@ -52,66 +53,68 @@ from ..config import hardware, set_us
 # 定数をローカル変数として定義（後方互換性のため）
 PCA9685_FREQUENCY = hardware.pca9685.FREQUENCY
 CH_ESC = hardware.pca9685.CH_ESC
 CH_SERVO = hardware.pca9685.CH_SERVO
 
 
 class PWMActuation:
     """
     PCA9685を使用したPWM制御によるActuation実装。
     func_explain.md の set_us() 関数を利用。
     """
     
     def __init__(self, i2c_address: int = 0x40):
         """
         初期化
         
         Args:
             i2c_address: PCA9685のI2Cアドレス（デフォルト: 0x40）
         """
         self.i2c_address = i2c_address
         self._calib: Optional[ActuationCalibration] = None
         self._pca: Optional[PCA9685] = None
         self._esc_channel = None
         self._servo_channel = None
         self._is_initialized = False
+        self._logger = logging.getLogger(self.__class__.__name__)
         
     def _initialize_hardware(self) -> None:
         """ハードウェアを初期化"""
         if self._is_initialized:
             return
         
         try:
             i2c = busio.I2C(board.SCL, board.SDA)
             self._pca = PCA9685(i2c, address=self.i2c_address)
             self._pca.frequency = PCA9685_FREQUENCY
             
             self._esc_channel = self._pca.channels[CH_ESC]
             self._servo_channel = self._pca.channels[CH_SERVO]
             
             self._is_initialized = True
         except Exception as e:
+            self._logger.exception("Failed to initialize PCA9685")
             raise RuntimeError(f"Failed to initialize PCA9685: {e}") from e
     
     def configure(self, calib: ActuationCalibration) -> None:
         """
         キャリブレーションを設定
         
         Args:
             calib: キャリブレーションパラメータ
         """
         self._calib = calib
         self._initialize_hardware()
         
         # 初期状態でニュートラル位置に設定
         if self._calib:
             set_us(self._esc_channel, self._calib.throttle_stop_us)
             set_us(self._servo_channel, self._calib.steer_center_us)
     
     def _steer_to_us(self, steer: float) -> int:
         """
         ステアリング値（-1.0 ～ 1.0）をμs値に変換
         
         Args:
             steer: ステアリング値（-1.0: 右、0.0: 中央、1.0: 左）
         
         Returns:
@@ -157,125 +160,128 @@ class PWMActuation:
         
         return us
     
     def apply(self, command: Command) -> Telemetry:
         """
         コマンドを適用
         
         Args:
             command: 制御コマンド
         
         Returns:
             テレメトリ情報
         """
         if not self._calib:
             return Telemetry(
                 frame_id=command.frame_id,
                 t_capture_sec=command.t_capture_sec,
                 status=ActuationStatus.CALIBRATION_ERROR,
                 message="Calibration not configured"
             )
         
         if not self._is_initialized:
             try:
                 self._initialize_hardware()
             except Exception as e:
+                self._logger.exception("Hardware initialization failed")
                 return Telemetry(
                     frame_id=command.frame_id,
                     t_capture_sec=command.t_capture_sec,
                     status=ActuationStatus.DRIVER_ERROR,
                     message=f"Hardware initialization failed: {e}"
                 )
         
         try:
             # STOPモードの場合は停止
             if command.mode == DriveMode.STOP:
                 throttle_us = self._calib.throttle_stop_us
                 applied_throttle = 0.0
             else:
                 # スロットル値を変換
                 throttle_us = self._throttle_to_us(command.throttle)
                 applied_throttle = command.throttle
             
             # ステアリング値を変換
             steer_us = self._steer_to_us(command.steer)
             applied_steer = command.steer
             
             # PWM信号を設定（func_explain.md の set_us() 関数を使用）
             set_us(self._esc_channel, throttle_us)
             set_us(self._servo_channel, steer_us)
             
             return Telemetry(
                 frame_id=command.frame_id,
                 t_capture_sec=command.t_capture_sec,
                 status=ActuationStatus.OK,
                 applied_steer=applied_steer,
                 applied_throttle=applied_throttle,
                 steer_pwm_us=steer_us,
                 throttle_pwm_us=throttle_us,
                 message=None
             )
         except Exception as e:
+            self._logger.exception("Failed to apply command")
             return Telemetry(
                 frame_id=command.frame_id,
                 t_capture_sec=command.t_capture_sec,
                 status=ActuationStatus.DRIVER_ERROR,
                 message=f"Failed to apply command: {e}"
             )
     
     def stop(self, reason: str = "emergency") -> Telemetry:
         """
         緊急停止
         
         Args:
             reason: 停止理由
         
         Returns:
             テレメトリ情報
         """
         if not self._calib or not self._is_initialized:
             return Telemetry(
                 frame_id=0,
                 t_capture_sec=0.0,
                 status=ActuationStatus.STOPPED,
                 message=reason
             )
         
         try:
             # ニュートラル位置に設定
             set_us(self._esc_channel, self._calib.throttle_stop_us)
             set_us(self._servo_channel, self._calib.steer_center_us)
             
             return Telemetry(
                 frame_id=0,
                 t_capture_sec=0.0,
                 status=ActuationStatus.STOPPED,
                 applied_steer=0.0,
                 applied_throttle=0.0,
                 steer_pwm_us=self._calib.steer_center_us,
                 throttle_pwm_us=self._calib.throttle_stop_us,
                 message=reason
             )
         except Exception as e:
+            self._logger.exception("Failed to stop")
             return Telemetry(
                 frame_id=0,
                 t_capture_sec=0.0,
                 status=ActuationStatus.DRIVER_ERROR,
                 message=f"Failed to stop: {e}"
             )
     
     def close(self) -> None:
         """リソースを解放"""
         # PCA9685のクリーンアップ（必要に応じて）
         if self._is_initialized:
             # 停止状態に設定
             try:
                 if self._calib:
                     set_us(self._esc_channel, self._calib.throttle_stop_us)
                     set_us(self._servo_channel, self._calib.steer_center_us)
             except Exception:
-                pass  # エラーは無視
+                self._logger.exception("Failed to reset PWM on close")
             
             self._is_initialized = False
             self._pca = None
             self._esc_channel = None
             self._servo_channel = None
