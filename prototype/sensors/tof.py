# --------------------------------
# sensors/tof.py
# TOFセンサー（VL53L0X）を読み取る実装
# 右、左、前の3つのセンサーをサポート
# --------------------------------
from __future__ import annotations

import os
import sys
import time
from typing import Optional, Tuple
from dataclasses import dataclass

from ..domain.distance import DistanceData

# ハードウェアモジュールのインポート（実機環境を優先、失敗時はモックを使用）
try:
    import board
    import busio
    import digitalio
    import adafruit_vl53l0x
except (ImportError, RuntimeError):
    # Docker環境などで実機モジュールが使用できない場合はモックを使用
    # sampleディレクトリをパスに追加
    test_code_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'sample')
    if test_code_path not in sys.path:
        sys.path.insert(0, test_code_path)
    
    import board_mock as board
    import busio_mock as busio
    import digitalio_mock as digitalio
    
    # adafruit_vl53l0x のモッククラス
    class VL53L0X:
        """VL53L0X TOFセンサーのモック実装"""
        def __init__(self, i2c, address=0x29):
            self.i2c = i2c
            self.address = address
            self._range = 1000  # デフォルト距離（mm）
            print(f"[MOCK] VL53L0X initialized: address=0x{address:02X}")
        
        def set_address(self, new_address):
            """I2Cアドレスを変更（モック）"""
            self.address = new_address
            print(f"[MOCK] VL53L0X address changed to 0x{new_address:02X}")
        
        @property
        def range(self):
            """距離を取得（モック）"""
            return self._range
    
    # モックモジュールとして登録
    class VL53L0XModule:
        VL53L0X = VL53L0X
    
    adafruit_vl53l0x = VL53L0XModule()
    print("[INFO] Using mock hardware modules for TOF sensor", file=sys.stderr)


@dataclass
class TOFReadings:
    """TOFセンサーの読み取り値"""
    front: int  # 前の距離（mm）
    left: int   # 左の距離（mm）
    right: int  # 右の距離（mm）


class TOFSensor:
    """
    TOFセンサー（VL53L0X）を読み取るクラス
    右、左、前の3つのセンサーをサポート
    """
    
    def __init__(
        self,
        xshut_pins: Tuple[int, int, int] = (17, 27, 22),
        i2c_addresses: Tuple[int, int, int] = (0x30, 0x31, 0x32)
    ):
        """
        初期化
        
        Args:
            xshut_pins: XSHUTピンのGPIO番号（前、左、右の順）
            i2c_addresses: I2Cアドレス（前、左、右の順、デフォルト: 0x30, 0x31, 0x32）
        """
        self.xshut_pins = xshut_pins
        self.i2c_addresses = i2c_addresses
        self._i2c: Optional[busio.I2C] = None
        self._sensors: list[adafruit_vl53l0x.VL53L0X] = []
        self._xshut_controls: list[digitalio.DigitalInOut] = []
        self._is_initialized = False
    
    def _initialize_hardware(self) -> None:
        """ハードウェアを初期化"""
        if self._is_initialized:
            return
        
        try:
            # I2Cバスを初期化
            self._i2c = busio.I2C(board.SCL, board.SDA)
            
            # 1. まず全てのセンサーをリセット状態（Low）にする
            for pin_num in self.xshut_pins:
                pin = digitalio.DigitalInOut(getattr(board, f"D{pin_num}"))
                pin.direction = digitalio.Direction.OUTPUT
                pin.value = False
                self._xshut_controls.append(pin)
            
            time.sleep(0.1)
            
            # 2. 1つずつ順番に起動してアドレスを書き換える
            for i, pin in enumerate(self._xshut_controls):
                pin.value = True  # そのセンサーだけ電源をONにする
                time.sleep(0.01)
                
                # 起動直後は 0x29 にいるので、それを捕まえる
                sensor = adafruit_vl53l0x.VL53L0X(self._i2c, address=0x29)
                
                # 重ならないようにアドレスを変えていく
                new_address = self.i2c_addresses[i]
                sensor.set_address(new_address)
                
                self._sensors.append(sensor)
                print(f"[TOF] センサー {i} ({'前' if i == 0 else '左' if i == 1 else '右'}) をアドレス {hex(new_address)} で初期化しました", file=sys.stderr)
            
            self._is_initialized = True
        except Exception as e:
            raise RuntimeError(f"Failed to initialize TOF sensors: {e}") from e
    
    def read_tof_readings(self) -> TOFReadings:
        """
        3つのTOFセンサーから距離を読み取る（TOFReadings形式）
        
        Returns:
            TOFReadings: 前、左、右の距離（mm）
        """
        if not self._is_initialized:
            self._initialize_hardware()
        
        # センサーが3つあることを確認
        if len(self._sensors) != 3:
            raise RuntimeError(f"Expected 3 sensors, but {len(self._sensors)} sensors are initialized")
        
        # 前、左、右の順で読み取り
        front = self._sensors[0].range
        left = self._sensors[1].range
        right = self._sensors[2].range
        
        return TOFReadings(front=front, left=left, right=right)
    
    def read(self) -> DistanceData:
        """
        3つのTOFセンサーから距離を読み取る（DistanceData形式）
        DistanceSensorModuleプロトコルに適合
        
        Returns:
            DistanceData: 前、左、右の距離データ（タイムスタンプ付き）
        """
        readings = self.read_tof_readings()
        return DistanceData.from_tof_readings(readings)
    
    def read_front(self) -> int:
        """前のセンサーから距離を読み取る（mm）"""
        if not self._is_initialized:
            self._initialize_hardware()
        return self._sensors[0].range
    
    def read_left(self) -> int:
        """左のセンサーから距離を読み取る（mm）"""
        if not self._is_initialized:
            self._initialize_hardware()
        return self._sensors[1].range
    
    def read_right(self) -> int:
        """右のセンサーから距離を読み取る（mm）"""
        if not self._is_initialized:
            self._initialize_hardware()
        return self._sensors[2].range
    
    def close(self) -> None:
        """リソースを解放"""
        # 必要に応じてクリーンアップ処理を追加
        self._sensors.clear()
        self._xshut_controls.clear()
        self._is_initialized = False
