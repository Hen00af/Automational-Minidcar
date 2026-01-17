"""
busio モジュールのモック実装
Docker環境（非Raspberry Pi）で使用
"""
import sys

class I2C:
    """I2Cバスのモック実装"""
    def __init__(self, scl, sda, frequency=400000):
        """
        I2Cバスの初期化（モック）
        
        Args:
            scl: SCLピン（board.SCL）
            sda: SDAピン（board.SDA）
            frequency: I2C周波数（デフォルト: 400kHz）
        """
        self.scl = scl
        self.sda = sda
        self.frequency = frequency
        print(f"[MOCK] I2C initialized: SCL={scl.id}, SDA={sda.id}, frequency={frequency}Hz")
    
    def scan(self):
        """I2Cバス上のデバイスをスキャン（モック）"""
        print("[MOCK] I2C scan: No devices found (mock mode)")
        return []
    
    def try_lock(self):
        """I2Cバスのロック試行（モック）"""
        return True
    
    def unlock(self):
        """I2Cバスのロック解除（モック）"""
        pass
    
    def readfrom_into(self, address, buffer, start=0, end=None):
        """I2Cからデータを読み取り（モック）"""
        print(f"[MOCK] I2C read from address 0x{address:02X}")
        return len(buffer)
    
    def writeto(self, address, buffer, start=0, end=None, stop=True):
        """I2Cにデータを書き込み（モック）"""
        print(f"[MOCK] I2C write to address 0x{address:02X}: {buffer[start:end]}")
        return len(buffer)

class SPI:
    """SPIバスのモック実装"""
    def __init__(self, clock, MOSI=None, MISO=None):
        self.clock = clock
        self.MOSI = MOSI
        self.MISO = MISO
        print(f"[MOCK] SPI initialized")

class UART:
    """UARTのモック実装"""
    def __init__(self, tx, rx, baudrate=9600, bits=8, parity=None, stop=1):
        self.tx = tx
        self.rx = rx
        self.baudrate = baudrate
        print(f"[MOCK] UART initialized: baudrate={baudrate}")

# モジュールとして使用できるように属性を設定
class BusioModule:
    """busio モジュールのモック"""
    I2C = I2C
    SPI = SPI
    UART = UART

sys.modules[__name__] = BusioModule()
