"""
モックアクチュエーター実装
"""
from __future__ import annotations

import time
from typing import Optional

from mock.actuation.mock_channel import MockChannel
from mock.config.constants import PWM_PERIOD_US, DUTY_CYCLE_MAX_VALUE, DEFAULT_LOG_INTERVAL_SEC
from mock.core.utils import get_logger, clamp, linear_interpolate
from mock.core.exceptions import CalibrationError

from act.domain.command import Command, DriveMode
from act.domain.actuation import ActuationCalibration, Telemetry, ActuationStatus
from act.interfaces.protocols import Actuation


class MockActuator(Actuation):
    """
    モックアクチュエータークラス
    
    実際のハードウェア制御は行わず、ログ出力のみを行う。
    Actuationプロトコルに適合。
    
    Attributes:
        _calib: キャリブレーションパラメータ
        _verbose: 詳細ログ出力フラグ
        _esc_channel: ESCチャンネル（モック）
        _servo_channel: サーボチャンネル（モック）
        _logger: ロガーインスタンス
        _last_command_log_time: 最後のコマンドログ出力時刻
    """
    
    def __init__(self, verbose: bool = False):
        """
        初期化
        
        Args:
            verbose: Trueの場合、詳細ログを出力する。デフォルトはFalse
        """
        self._calib: Optional[ActuationCalibration] = None
        self._verbose = verbose
        self._esc_channel = MockChannel("esc", verbose=verbose)
        self._servo_channel = MockChannel("servo", verbose=verbose)
        self._logger = get_logger("mock.actuator")
        self._last_command_log_time = 0.0
    
    def configure(self, calib: ActuationCalibration) -> None:
        """
        キャリブレーションを設定
        
        Args:
            calib: キャリブレーションパラメータ
        
        Raises:
            ValueError: calibがNoneの場合
        """
        if calib is None:
            raise ValueError("calib must not be None")
        
        self._calib = calib
        if self._verbose:
            self._logger.info(
                "Actuation configured: Steer: center=%dμs, left=%dμs, right=%dμs, "
                "Throttle: stop=%dμs, max=%dμs",
                calib.steer_center_us,
                calib.steer_left_us,
                calib.steer_right_us,
                calib.throttle_stop_us,
                calib.throttle_max_us
            )
    
    def _steer_to_us(self, steer: float) -> int:
        """
        ステアリング値（-1.0 ～ 1.0）をμs値に変換
        
        Args:
            steer: ステアリング値（-1.0: 右、0.0: 中央、1.0: 左）
        
        Returns:
            マイクロ秒値
        
        Raises:
            CalibrationError: キャリブレーションが設定されていない場合
        """
        if not self._calib:
            raise CalibrationError("Calibration not configured. Call configure() first.")
        
        # リミットを適用
        steer_clamped = clamp(steer, -self._calib.steer_limit, self._calib.steer_limit)
        
        # 線形補間: steer=-1.0 -> steer_right_us, steer=0.0 -> steer_center_us, steer=1.0 -> steer_left_us
        if steer_clamped >= 0:
            # 中央から左へ
            us = int(linear_interpolate(
                steer_clamped,
                0.0, 1.0,
                self._calib.steer_center_us, self._calib.steer_left_us
            ))
        else:
            # 中央から右へ
            us = int(linear_interpolate(
                abs(steer_clamped),
                0.0, 1.0,
                self._calib.steer_center_us, self._calib.steer_right_us
            ))
        
        return us
    
    def _throttle_to_us(self, throttle: float) -> int:
        """
        スロットル値（0.0 ～ 1.0）をμs値に変換
        
        Args:
            throttle: スロットル値（0.0: 停止、1.0: 最大）
        
        Returns:
            マイクロ秒値
        
        Raises:
            CalibrationError: キャリブレーションが設定されていない場合
        """
        if not self._calib:
            raise CalibrationError("Calibration not configured. Call configure() first.")
        
        # リミットを適用
        throttle_clamped = clamp(throttle, 0.0, self._calib.throttle_limit)
        
        # 線形補間: throttle=0.0 -> throttle_stop_us, throttle=1.0 -> throttle_max_us
        us = int(linear_interpolate(
            throttle_clamped,
            0.0, 1.0,
            self._calib.throttle_stop_us, self._calib.throttle_max_us
        ))
        
        return us
    
    def _set_us(self, channel: MockChannel, us: int) -> None:
        """
        μs（マイクロ秒）をduty_cycle値に変換してチャンネルに設定
        
        Args:
            channel: モックチャンネルオブジェクト
            us: パルス幅（マイクロ秒）
        """
        duty_cycle = int(us / PWM_PERIOD_US * DUTY_CYCLE_MAX_VALUE)
        channel.duty_cycle = duty_cycle
    
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
            
            # モックチャンネル経由でログ出力される
            self._set_us(self._servo_channel, steer_us)
            self._set_us(self._esc_channel, throttle_us)
            
            # コマンド情報を1行でログ出力（頻度制限はMockChannelで行う）
            if self._verbose:
                current_time = time.time()
                if current_time - self._last_command_log_time >= DEFAULT_LOG_INTERVAL_SEC:
                    mode_str = command.mode.value if hasattr(command.mode, 'value') else str(command.mode)
                    self._logger.debug(
                        "Command (frame #%d): mode=%s, steer=%.2f, throttle=%.2f, reason=%s",
                        command.frame_id,
                        mode_str,
                        applied_steer,
                        applied_throttle,
                        command.reason
                    )
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
        except CalibrationError as e:
            return Telemetry(
                frame_id=command.frame_id,
                t_capture_sec=command.t_capture_sec,
                status=ActuationStatus.CALIBRATION_ERROR,
                message=str(e)
            )
        except Exception as e:
            self._logger.error("Failed to apply command: %s", e, exc_info=True)
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
        
        self._logger.warning("Emergency stop: %s", reason)
        self._set_us(self._servo_channel, steer_us)
        self._set_us(self._esc_channel, throttle_us)
        
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
        """
        リソースを解放
        
        モック実装では実際のリソースは使用していないが、
        インターフェースの一貫性のために実装されている。
        """
        if self._verbose:
            self._logger.info("Actuation closed")
        self._calib = None
        self._esc_channel = None
        self._servo_channel = None
