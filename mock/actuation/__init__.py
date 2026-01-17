# actuation パッケージ
# コマンドを物理信号（PWM等）に変換・出力する駆動モジュールの実装

from .mock_actuator import MockActuator
from .mock_channel import MockChannel

__all__ = ["MockActuator", "MockChannel"]
