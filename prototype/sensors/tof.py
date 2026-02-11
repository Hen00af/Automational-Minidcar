# --------------------------------
# sensors/tof.py
# TOFセンサー（VL53L0X）を読み取る実装
# 左前、左、前の3つのセンサーをサポート
# --------------------------------
from __future__ import annotations

import sys
import time
from typing import Optional, Tuple
from dataclasses import dataclass

from ..domain.distance import DistanceData
from ..config import timing, sensors

# ハードウェアモジュールのインポート（ラズベリーパイ環境専用）
import board
import busio
import digitalio
import adafruit_vl53l0x

# 範囲外を示すデフォルト値（mm）
_OUT_OF_RANGE: int = 8190


@dataclass
class TOFReadings:
    """TOFセンサーの読み取り値"""
    front: int  # 前の距離（mm）
    left: int   # 左の距離（mm）
    left_front: int  # 左前の距離（mm）


class TOFSensor:
    """
    TOFセンサー（VL53L0X）を読み取るクラス
    左前、左、前の3つのセンサーをサポート
    """
    
    def __init__(
        self,
        xshut_pins: Tuple[int, int, int] = sensors.vl53l0x.XSHUT_PINS,
        i2c_addresses: Tuple[int, int, int] = sensors.vl53l0x.I2C_ADDRESSES
    ):
        """
        初期化
        
        Args:
            xshut_pins: XSHUTピンのGPIO番号（前、左、左前の順）。デフォルトは設定ファイルの値
            i2c_addresses: I2Cアドレス（前、左、左前の順）。デフォルトは設定ファイルの値
        """
        self.xshut_pins = xshut_pins
        self.i2c_addresses = i2c_addresses
        self._i2c: Optional[busio.I2C] = None
        self._sensors: list[adafruit_vl53l0x.VL53L0X] = []
        self._xshut_controls: list[digitalio.DigitalInOut] = []
        self._is_initialized = False
        self._last_readings = TOFReadings(
            front=_OUT_OF_RANGE, left=_OUT_OF_RANGE, left_front=_OUT_OF_RANGE
        )
    
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
            
            time.sleep(timing.sensor_init.RESET_WAIT)
            
            # 2. 1つずつ順番に起動してアドレスを書き換える
            for i, pin in enumerate(self._xshut_controls):
                pin.value = True  # そのセンサーだけ電源をONにする
                time.sleep(timing.sensor_init.WAKE_WAIT)
                
                # 起動直後はデフォルトアドレスにいるので、それを捕まえる
                sensor = adafruit_vl53l0x.VL53L0X(self._i2c, address=sensors.vl53l0x.DEFAULT_ADDRESS)
                
                # センサーの計測時間を設定（設定ファイルから取得）
                sensor.measurement_timing_budget = sensors.vl53l0x.MEASUREMENT_TIMING_BUDGET
                
                # 重ならないようにアドレスを変えていく
                new_address = self.i2c_addresses[i]
                sensor.set_address(new_address)
                
                self._sensors.append(sensor)
                sensor_name = sensors.vl53l0x.SENSOR_NAMES[i] if i < len(sensors.vl53l0x.SENSOR_NAMES) else f"センサー{i}"
                print(f"[TOF] センサー {i} ({sensor_name}) をアドレス {hex(new_address)} で初期化しました", file=sys.stderr)
            
            self._is_initialized = True
            self.start_continuous()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize TOF sensors: {e}") from e
    
    def read_tof_readings(self) -> TOFReadings:
        """
        3つのTOFセンサーから距離を読み取る（TOFReadings形式）
        
        Returns:
            TOFReadings: 前、左、左前の距離（mm）
        """
        if not self._is_initialized:
            self._initialize_hardware()
        
        # センサー数が期待値と一致することを確認
        expected_count = sensors.vl53l0x.NUM_SENSORS
        if len(self._sensors) != expected_count:
            raise RuntimeError(f"Expected {expected_count} sensors, but {len(self._sensors)} sensors are initialized")
        
        # 前、左、左前の順でループして読み取り
        readings_list = []
        for sensor in self._sensors:
            readings_list.append(sensor.range)
        
        # TOFReadings形式に変換（現在は3つのセンサーを想定）
        if len(readings_list) >= 3:
            return TOFReadings(front=readings_list[0], left=readings_list[1], left_front=readings_list[2])
        else:
            raise RuntimeError(f"Expected at least 3 sensor readings, but got {len(readings_list)}")
    
    def read(self) -> DistanceData:
        """
        3つのTOFセンサーから距離を読み取る（DistanceData形式）
        DistanceSensorModuleプロトコルに適合
        
        Returns:
            DistanceData: 前、左、左前の距離データ（タイムスタンプ付き）
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
    
    def read_left_front(self) -> int:
        """左前のセンサーから距離を読み取る（mm）"""
        if not self._is_initialized:
            self._initialize_hardware()
        return self._sensors[2].range
    
    def start_continuous(self) -> None:
        """全センサーを連続計測モードに切り替える"""
        if not self._is_initialized:
            self._initialize_hardware()
            return  # _initialize_hardware 内で start_continuous が呼ばれる
        for sensor in self._sensors:
            sensor.start_continuous()
        print("[TOF] 連続計測モードを開始しました", file=sys.stderr)

    def stop_continuous(self) -> None:
        """全センサーの連続計測モードを停止する"""
        for sensor in self._sensors:
            sensor.stop_continuous()
        print("[TOF] 連続計測モードを停止しました", file=sys.stderr)

    def poll(self) -> tuple[bool, DistanceData]:
        """
        data-readyなセンサーのみ読み出し、更新有無と最新のDistanceDataを返す。
        readyでないセンサーは前回値を保持する。

        Returns:
            (updated, distance_data): 1台でも更新があればupdated=True
        """
        if not self._is_initialized:
            self._initialize_hardware()

        updated = False
        # front=0, left=1, left_front=2
        if self._sensors[0].data_ready:
            self._last_readings.front = self._sensors[0].range
            updated = True
        if self._sensors[1].data_ready:
            self._last_readings.left = self._sensors[1].range
            updated = True
        if self._sensors[2].data_ready:
            self._last_readings.left_front = self._sensors[2].range
            updated = True

        return updated, DistanceData.from_tof_readings(self._last_readings)

    def close(self) -> None:
        """リソースを解放"""
        if self._is_initialized:
            self.stop_continuous()
        self._sensors.clear()
        self._xshut_controls.clear()
        self._is_initialized = False
