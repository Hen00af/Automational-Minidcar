"""
digitalio モジュールのモック実装
Docker環境（非Raspberry Pi）で使用
"""
import sys

class Direction:
    """ピンの方向"""
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

class Pull:
    """プルアップ/プルダウン"""
    UP = "UP"
    DOWN = "DOWN"
    NONE = None

class DigitalInOut:
    """デジタルI/Oピンのモック実装"""
    def __init__(self, pin):
        """
        デジタルI/Oピンの初期化（モック）
        
        Args:
            pin: board モジュールのピンオブジェクト
        """
        self.pin = pin
        self._direction = None
        self._pull = None
        self._value = None
        print(f"[MOCK] DigitalInOut initialized: pin={pin.id if hasattr(pin, 'id') else pin}")
    
    @property
    def direction(self):
        """ピンの方向を取得"""
        return self._direction
    
    @direction.setter
    def direction(self, value):
        """ピンの方向を設定"""
        self._direction = value
        print(f"[MOCK] DigitalInOut direction set to: {value}")
    
    @property
    def pull(self):
        """プルアップ/プルダウン設定を取得"""
        return self._pull
    
    @pull.setter
    def pull(self, value):
        """プルアップ/プルダウン設定を設定"""
        self._pull = value
        print(f"[MOCK] DigitalInOut pull set to: {value}")
    
    @property
    def value(self):
        """ピンの値を取得"""
        return self._value
    
    @value.setter
    def value(self, val):
        """ピンの値を設定"""
        self._value = val
        print(f"[MOCK] DigitalInOut value set to: {val}")
    
    def deinit(self):
        """ピンのクリーンアップ（モック）"""
        print(f"[MOCK] DigitalInOut deinit: pin={self.pin.id if hasattr(self.pin, 'id') else self.pin}")

# モジュールとして使用できるように属性を設定
class DigitalioModule:
    """digitalio モジュールのモック"""
    Direction = Direction
    Pull = Pull
    DigitalInOut = DigitalInOut

sys.modules[__name__] = DigitalioModule()
