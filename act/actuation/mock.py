# --------------------------------
# actuation/mock.py
# モック実装（開発・テスト用）
# --------------------------------
from __future__ import annotations

import time
from typing import Optional

from ..domain.command import Command, DriveMode
from ..domain.actuation import ActuationCalibration, Telemetry, ActuationStatus
from ..interfaces.protocols import Actuation
from ..config import hardware, set_us


class MockChannel:
    """モックチャンネルオブジェクト（set_us()関数で使用）"""
    def __init__(self, name: str, log_interval_sec: float = 1.0, verbose: bool = False):
        self.name = name
        self._duty_cycle = 0
        self._log_interval_sec = log_interval_sec
        self._last_log_time = 0.0
        self._update_count = 0
        self._verbose = verbose
    
    @property
    def duty_cycle(self) -> int:
        return self._duty_cycle
    
    @duty_cycle.setter
    def duty_cycle(self, value: int) -> None:
        self._duty_cycle = value
        self._update_count += 1
        
        # ログ出力頻度を制限（一定時間ごとに出力）
        current_time = time.time()
        if self._verbose and current_time - self._last_log_time >= self._log_interval_sec:
            us = int(value / hardware.pca9685.DUTY_CYCLE_MAX_VALUE * hardware.pca9685.PWM_PERIOD_US)
            print(f"[MOCK] set_us({self.name}, {us}μs)  # duty_cycle={value} (updates: {self._update_count})")
            self._last_log_time = current_time


class MockActuation:
    """
    モック実装（実際のハードウェア制御は行わず、config.utilsのset_us()関数を使用）
    func_explain.md の set_us() 関数の動作をシミュレート
    """
    
    def __init__(self, verbose: bool = False):
        """
        初期化
        
        Args:
            verbose: Trueの場合、詳細ログを出力する。デフォルトはFalse
        """
        self._calib: Optional[ActuationCalibration] = None
        self._verbose = verbose
        # モックチャンネルオブジェクトを作成
        self._esc_channel = MockChannel("esc", verbose=verbose)
        self._servo_channel = MockChannel("servo", verbose=verbose)
    
    def configure(self, calib: ActuationCalibration) -> None:
        """
        キャリブレーションを設定
        
        Args:
            calib: キャリブレーションパラメータ
        """
        self._calib = calib
        if self._verbose:
            print(f"[MOCK] Actuation configured:")
            print(f"  Steer: center={calib.steer_center_us}μs, left={calib.steer_left_us}μs, right={calib.steer_right_us}μs")
            print(f"  Throttle: stop={calib.throttle_stop_us}μs, max={calib.throttle_max_us}μs")
    
    def _steer_to_us(self, steer: float) -> int:
        """
        ステアリング値（-1.0 ～ 1.0）をμs値に変換
        
        Args:
            steer: ステアリング値（-1.0: 右、0.0: 中央、1.0: 左）
        
        Returns:
            マイクロ秒値
        """
        if not self._calib:
            raise RuntimeError("Calibration not configured. Call configure() first.")
        
        # リミットを適用
        steer = max(min(steer, self._calib.steer_limit), -self._calib.steer_limit)
        
        # 線形補間: steer=-1.0 -> steer_right_us, steer=0.0 -> steer_center_us, steer=1.0 -> steer_left_us
        if steer >= 0:
            # 中央から左へ
            us = int(self._calib.steer_center_us + 
                    (self._calib.steer_left_us - self._calib.steer_center_us) * steer)
        else:
            # 中央から右へ
            us = int(self._calib.steer_center_us + 
                    (self._calib.steer_right_us - self._calib.steer_center_us) * abs(steer))
        
        return us
    
    def _throttle_to_us(self, throttle: float) -> int:
        """
        スロットル値（0.0 ～ 1.0）をμs値に変換
        
        Args:
            throttle: スロットル値（0.0: 停止、1.0: 最大）
        
        Returns:
            マイクロ秒値
        """
        if not self._calib:
            raise RuntimeError("Calibration not configured. Call configure() first.")
        
        # リミットを適用
        throttle = max(min(throttle, self._calib.throttle_limit), 0.0)
        
        # 線形補間: throttle=0.0 -> throttle_stop_us, throttle=1.0 -> throttle_max_us
        us = int(self._calib.throttle_stop_us + 
                (self._calib.throttle_max_us - self._calib.throttle_stop_us) * throttle)
        
        return us
    
    def apply(self, command: Command) -> Telemetry:
        """
        コマンドを適用（モック：ログ出力のみ）
        
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
            
            # config.utilsのset_us()関数を使用（モックチャンネル経由でログ出力される）
            set_us(self._servo_channel, steer_us)
            set_us(self._esc_channel, throttle_us)
            
            # コマンド情報を1行でログ出力（頻度制限はMockChannelで行う）
            current_time = time.time()
            if not hasattr(self, '_last_command_log_time'):
                self._last_command_log_time = 0.0
            if self._verbose and current_time - self._last_command_log_time >= 1.0:
                mode_str = command.mode.value if hasattr(command.mode, 'value') else str(command.mode)
                print(f"[MOCK] Command (frame #{command.frame_id}): mode={mode_str}, steer={applied_steer:.2f}, throttle={applied_throttle:.2f}, reason={command.reason}")
                self._last_command_log_time = current_time
            
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
            return Telemetry(
                frame_id=command.frame_id,
                t_capture_sec=command.t_capture_sec,
                status=ActuationStatus.DRIVER_ERROR,
                message=f"Failed to apply command: {e}"
            )
    
    def stop(self, reason: str = "emergency") -> Telemetry:
        """
        緊急停止（モック）
        
        Args:
            reason: 停止理由
        
        Returns:
            テレメトリ情報
        """
        if not self._calib:
            return Telemetry(
                frame_id=0,
                t_capture_sec=0.0,
                status=ActuationStatus.STOPPED,
                message=reason
            )
        
        # ニュートラル位置に設定
        steer_us = self._calib.steer_center_us
        throttle_us = self._calib.throttle_stop_us
        
        print(f"[MOCK] Emergency stop: {reason}")
        # config.utilsのset_us()関数を使用
        set_us(self._servo_channel, steer_us)
        set_us(self._esc_channel, throttle_us)
        
        return Telemetry(
            frame_id=0,
            t_capture_sec=0.0,
            status=ActuationStatus.STOPPED,
            applied_steer=0.0,
            applied_throttle=0.0,
            steer_pwm_us=steer_us,
            throttle_pwm_us=throttle_us,
            message=reason
        )
    
    def close(self) -> None:
        """リソースを解放（モック：何もしない）"""
        print("[MOCK] Actuation closed")
        self._calib = None
        self._esc_channel = None
        self._servo_channel = None
