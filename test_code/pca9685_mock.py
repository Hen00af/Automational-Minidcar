"""
adafruit_pca9685 のモック実装
Docker環境（非Raspberry Pi）で使用
"""
import sys

class PCAChannel:
    """PCA9685のチャンネルのモック実装"""
    def __init__(self, channel_num, pca):
        self.channel_num = channel_num
        self.pca = pca
        self._duty_cycle = 0
    
    @property
    def duty_cycle(self):
        """現在のduty_cycle値を取得"""
        return self._duty_cycle
    
    @duty_cycle.setter
    def duty_cycle(self, value):
        """duty_cycle値を設定（モック）"""
        self._duty_cycle = value
        # duty_cycleをμsに変換（16bit値、20ms周期を想定）
        us = int(value / 65535 * 20000)
        print(f"[MOCK] PCA9685 Channel {self.channel_num}: duty_cycle=0x{value:04X} ({value}/65535) = {us}μs")

class PCA9685:
    """PCA9685 PWMドライバーのモック実装"""
    def __init__(self, i2c, address=0x40):
        """
        PCA9685の初期化（モック）
        
        Args:
            i2c: I2Cバスオブジェクト
            address: I2Cアドレス（デフォルト: 0x40）
        """
        self.i2c = i2c
        self.address = address
        self._frequency = 50
        self._channels = [PCAChannel(i, self) for i in range(16)]
        print(f"[MOCK] PCA9685 initialized: address=0x{address:02X}, frequency={self._frequency}Hz")
    
    @property
    def frequency(self):
        """PWM周波数を取得"""
        return self._frequency
    
    @frequency.setter
    def frequency(self, value):
        """PWM周波数を設定"""
        self._frequency = value
        print(f"[MOCK] PCA9685 frequency set to {value}Hz")
    
    @property
    def channels(self):
        """チャンネルリストを取得"""
        return self._channels
    
    def __getitem__(self, index):
        """チャンネルにインデックスでアクセス"""
        return self._channels[index]

# モジュールとして使用できるように属性を設定
class PCA9685Module:
    """adafruit_pca9685 モジュールのモック"""
    PCA9685 = PCA9685

sys.modules[__name__] = PCA9685Module()
