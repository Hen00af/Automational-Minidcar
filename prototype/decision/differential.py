# --------------------------------
# decision/differential.py
# D制御（微分制御）の実装
# --------------------------------
from __future__ import annotations

import time
from typing import Optional


class DifferentialController:
    """
    D制御（微分制御）の実装
    
    誤差の変化率を計算し、急激な変化を抑制します。
    誤差が急に変化すると微分値が大きくなり、過剰な応答を抑制します。
    """
    
    def __init__(
        self,
        kd: float = 0.0,
        smoothing_factor: float = 0.0
    ):
        """
        初期化
        
        Args:
            kd: D制御の微分ゲイン。デフォルトは0.0（無効）
            smoothing_factor: 微分値の平滑化係数 [0.0, 1.0]
                              0.0: 平滑化なし（前回の微分値を使用しない）
                              1.0: 完全に前回の値を保持
        """
        self.kd = kd
        self.smoothing_factor = max(0.0, min(1.0, smoothing_factor))
        
        # 前回の誤差
        self._prev_error: Optional[float] = None
        
        # 前回のタイムスタンプ
        self._prev_time: Optional[float] = None
        
        # 平滑化された微分値
        self._smoothed_derivative: float = 0.0
    
    def update(self, error: float, current_time: Optional[float] = None) -> float:
        """
        誤差を更新し、微分値を計算
        
        Args:
            error: 現在の誤差
            current_time: 現在時刻（秒）。Noneの場合は自動取得
            
        Returns:
            float: 微分制御項（kd * derivative）
        """
        if current_time is None:
            current_time = time.time()
        
        # 初回呼び出し時は微分を0として返す
        if self._prev_time is None or self._prev_error is None:
            self._prev_time = current_time
            self._prev_error = error
            self._smoothed_derivative = 0.0
            return 0.0
        
        # 時間差分を計算
        dt = current_time - self._prev_time
        
        # 時間差分が0以下または異常に大きい場合はスキップ
        if dt <= 0.0 or dt > 1.0:
            self._prev_time = current_time
            self._prev_error = error
            return self.kd * self._smoothed_derivative
        
        # 誤差の変化量を計算
        error_change = error - self._prev_error
        
        # 微分値（誤差の変化率）を計算
        # derivative = d(error)/dt = (error - prev_error) / dt
        derivative = error_change / dt
        
        # 平滑化を適用（指数移動平均）
        # smoothed = smoothing_factor * prev_smoothed + (1 - smoothing_factor) * current
        self._smoothed_derivative = (
            self.smoothing_factor * self._smoothed_derivative +
            (1.0 - self.smoothing_factor) * derivative
        )
        
        # 前回値を更新
        self._prev_time = current_time
        self._prev_error = error
        
        # D制御項を返す
        return self.kd * self._smoothed_derivative
    
    def reset(self) -> None:
        """
        微分値をリセット
        """
        self._prev_error = None
        self._prev_time = None
        self._smoothed_derivative = 0.0
    
    def get_derivative_value(self) -> float:
        """
        現在の微分値（誤差の変化率）を取得
        
        Returns:
            float: 現在の微分値
        """
        return self._smoothed_derivative
    
    def get_differential_term(self) -> float:
        """
        現在の微分制御項を取得（kd * derivative）
        
        Returns:
            float: 微分制御項
        """
        return self.kd * self._smoothed_derivative
