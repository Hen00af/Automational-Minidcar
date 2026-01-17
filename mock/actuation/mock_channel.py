"""
モックチャンネル実装
"""
from __future__ import annotations

import time
from mock.config.constants import PWM_PERIOD_US, DUTY_CYCLE_MAX_VALUE, DEFAULT_LOG_INTERVAL_SEC
from mock.core.utils import get_logger


class MockChannel:
    """
    モックチャンネルオブジェクト
    
    PWM制御のシミュレーション用。duty_cycle値を保持し、
    ログ出力を行う。
    
    Attributes:
        name: チャンネル名（"esc" または "servo"）
        _duty_cycle: duty_cycle値
        _log_interval_sec: ログ出力間隔（秒）
        _last_log_time: 最後のログ出力時刻
        _update_count: 更新回数
        _verbose: 詳細ログ出力フラグ
        _logger: ロガーインスタンス
    """
    
    def __init__(
        self,
        name: str,
        log_interval_sec: float = DEFAULT_LOG_INTERVAL_SEC,
        verbose: bool = False
    ):
        """
        初期化
        
        Args:
            name: チャンネル名（"esc" または "servo"）
            log_interval_sec: ログ出力間隔（秒）
            verbose: Trueの場合、詳細ログを出力する
        """
        self.name = name
        self._duty_cycle = 0
        self._log_interval_sec = log_interval_sec
        self._last_log_time = 0.0
        self._update_count = 0
        self._verbose = verbose
        self._logger = get_logger(f"mock.channel.{name}")
    
    @property
    def duty_cycle(self) -> int:
        """
        duty_cycle値を取得
        
        Returns:
            duty_cycle値
        """
        return self._duty_cycle
    
    @duty_cycle.setter
    def duty_cycle(self, value: int) -> None:
        """
        duty_cycle値を設定
        
        Args:
            value: 設定するduty_cycle値
        """
        self._duty_cycle = value
        self._update_count += 1
        
        # ログ出力頻度を制限（一定時間ごとに出力）
        if self._verbose:
            current_time = time.time()
            if current_time - self._last_log_time >= self._log_interval_sec:
                us = int(value / DUTY_CYCLE_MAX_VALUE * PWM_PERIOD_US)
                self._logger.debug(
                    "set_us(%s, %dμs)  # duty_cycle=%d (updates: %d)",
                    self.name,
                    us,
                    value,
                    self._update_count
                )
                self._last_log_time = current_time
