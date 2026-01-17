"""
board モジュールのモック実装
Docker環境（非Raspberry Pi）で使用
"""
import sys

# モック用のピンオブジェクト
class Pin:
    """GPIOピンのモック"""
    def __init__(self, pin_id):
        self.id = pin_id

# board モジュールの属性を定義
class Board:
    """board モジュールのモック"""
    # I2C用のピン（標準的なRaspberry Piのピン番号）
    SCL = Pin(3)  # GPIO 3 (Physical pin 5)
    SDA = Pin(2)  # GPIO 2 (Physical pin 3)
    
    # その他のGPIOピン（必要に応じて追加）
    D2 = SDA
    D3 = SCL
    D17 = Pin(17)
    D27 = Pin(27)
    D22 = Pin(22)
    
    def __getattr__(self, name):
        """動的にピン属性を生成（例: D4, D5, ...）"""
        if name.startswith('D') and name[1:].isdigit():
            pin_num = int(name[1:])
            pin = Pin(pin_num)
            setattr(self, name, pin)  # キャッシュ
            return pin
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

# モジュールとして使用できるように属性を設定
sys.modules[__name__] = Board()
