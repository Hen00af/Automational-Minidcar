"""
ユーティリティ関数モジュール
共通で使用するユーティリティ関数を定義
"""
import logging
from typing import Optional

# ロガーの設定
_logger: Optional[logging.Logger] = None


def get_logger(name: str = "mock") -> logging.Logger:
    """
    ロガーを取得（シングルトンパターン）
    
    Args:
        name: ロガー名
    
    Returns:
        ロガーインスタンス
    """
    global _logger
    if _logger is None:
        _logger = logging.getLogger(name)
        if not _logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '[%(levelname)s] %(name)s: %(message)s'
            )
            handler.setFormatter(formatter)
            _logger.addHandler(handler)
            _logger.setLevel(logging.INFO)
    return _logger


def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    値を指定範囲内にクランプ
    
    Args:
        value: クランプする値
        min_value: 最小値
        max_value: 最大値
    
    Returns:
        クランプされた値
    """
    return max(min(value, max_value), min_value)


def linear_interpolate(
    value: float,
    input_min: float,
    input_max: float,
    output_min: float,
    output_max: float
) -> float:
    """
    線形補間を行う
    
    Args:
        value: 入力値
        input_min: 入力の最小値
        input_max: 入力の最大値
        output_min: 出力の最小値
        output_max: 出力の最大値
    
    Returns:
        補間された値
    """
    if input_max == input_min:
        return output_min
    
    normalized = (value - input_min) / (input_max - input_min)
    return output_min + normalized * (output_max - output_min)
