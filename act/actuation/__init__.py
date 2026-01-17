# actuation パッケージ
# コマンドを物理信号（PWM等）に変換・出力する駆動モジュールの実装

from ..mock.actuation import MockActuation

# pwm.pyのインポートは条件付き（実機環境でのみ利用可能）
try:
    from .pwm import PWMActuation
    __all__ = [
        "PWMActuation",
        "MockActuation",
    ]
except ImportError:
    # モック環境ではPWMActuationは利用不可
    __all__ = [
        "MockActuation",
    ]
