# actuation パッケージ
# コマンドを物理信号（PWM等）に変換・出力する駆動モジュールの実装

# pwm.pyのインポートは条件付き（実機環境でのみ利用可能）
try:
    from .pwm import PWMActuation
    __all__ = [
        "PWMActuation",
    ]
except ImportError:
    # ハードウェアモジュールが利用できない場合
    __all__ = []
