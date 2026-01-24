# コードとして持っているが、使用していない。

# --------------------------------
# decision/integral.py
# I制御（積分制御）の実装
# --------------------------------
from __future__ import annotations

import time
from typing import Optional


class IntegralController:
    """
    I制御（積分制御）の実装
    
    誤差の積分を計算し、累積誤差による定常偏差を補正します。
    誤差が長時間続くと積分値が大きくなり、より強い補正をかけます。
    """
    
    def __init__(
        self,
        ki: float = 0.0,
        integral_limit: Optional[float] = None,
        reset_on_zero_crossing: bool = False
    ):
        """
        初期化
        
        Args:
            ki: I制御の積分ゲイン。デフォルトは0.0（無効）
            integral_limit: 積分値の上限（絶対値）。Noneの場合は制限なし
            reset_on_zero_crossing: 誤差の符号が変わったときに積分をリセットするか
        """
        self.ki = ki
        self.integral_limit = integral_limit
        self.reset_on_zero_crossing = reset_on_zero_crossing
        
        # 積分値の累積
        self._integral_error: float = 0.0
        
        # 前回の誤差（符号変化検出用）
        self._prev_error: Optional[float] = None
        
        # 前回のタイムスタンプ（時間ベースの積分用）
        self._prev_time: Optional[float] = None
    
    def update(self, error: float, current_time: Optional[float] = None) -> float:
        """
        誤差を更新し、積分値を計算
        
        Args:
            error: 現在の誤差
            current_time: 現在時刻（秒）。Noneの場合は自動取得
            
        Returns:
            float: 積分制御項（ki * integral_error）
        """
        if current_time is None:
            current_time = time.time()
        
        # 初回呼び出し時は積分を開始
        if self._prev_time is None:
            self._prev_time = current_time
            self._prev_error = error
            return 0.0
        
        # 時間差分を計算
        dt = current_time - self._prev_time
        
        # 時間差分が0以下または異常に大きい場合はスキップ
        if dt <= 0.0 or dt > 1.0:
            self._prev_time = current_time
            self._prev_error = error
            return self.ki * self._integral_error
        
        # 符号変化の検出とリセット
        if self.reset_on_zero_crossing and self._prev_error is not None:
            if (self._prev_error > 0 and error < 0) or (self._prev_error < 0 and error > 0):
                # 誤差の符号が変わったので積分をリセット
                self._integral_error = 0.0
        
        # 積分値を更新（矩形積分）
        # integral += error * dt
        self._integral_error += error * dt
        
        # 積分値の制限
        if self.integral_limit is not None:
            self._integral_error = max(
                min(self._integral_error, self.integral_limit),
                -self.integral_limit
            )
        
        # 前回値を更新
        self._prev_time = current_time
        self._prev_error = error
        
        # I制御項を返す
        return self.ki * self._integral_error
    
    def reset(self) -> None:
        """
        積分値をリセット
        """
        self._integral_error = 0.0
        self._prev_error = None
        self._prev_time = None
    
    def get_integral_value(self) -> float:
        """
        現在の積分値を取得
        
        Returns:
            float: 現在の積分値
        """
        return self._integral_error
    
    def get_integral_term(self) -> float:
        """
        現在の積分制御項を取得（ki * integral_error）
        
        Returns:
            float: 積分制御項
        """
        return self.ki * self._integral_error
