# --------------------------------
# sensors/mock.py
# TOFセンサーのモック実装（開発・テスト用）
# --------------------------------
from __future__ import annotations

import math
import random
import time
from typing import Optional, Tuple

from .tof import TOFReadings
from ..domain.distance import DistanceData


class MockTOFSensor:
    """
    TOFセンサーのモック実装（実際のハードウェアは使用せず、固定値やランダム値を返す）
    右、左、前の3つのセンサーをサポート
    """
    
    def __init__(
        self,
        xshut_pins: Tuple[int, int, int] = (17, 27, 22),
        i2c_addresses: Tuple[int, int, int] = (0x30, 0x31, 0x32),
        front_distance: Optional[int] = None,
        left_distance: Optional[int] = None,
        right_distance: Optional[int] = None,
        use_random: bool = False,
        random_range: Tuple[int, int] = (50, 2000),
        log_interval_sec: float = 1.0,
        use_dynamic: bool = False
    ):
        """
        初期化
        
        Args:
            xshut_pins: XSHUTピンのGPIO番号（前、左、右の順）（モックでは使用しない）
            i2c_addresses: I2Cアドレス（前、左、右の順）（モックでは使用しない）
            front_distance: 前のセンサーの固定距離（mm）。Noneの場合はランダム
            left_distance: 左のセンサーの固定距離（mm）。Noneの場合はランダム
            right_distance: 右のセンサーの固定距離（mm）。Noneの場合はランダム
            use_random: Trueの場合、固定値があってもランダム値を返す
            random_range: ランダム値の範囲（最小値、最大値）mm
            log_interval_sec: ログ出力間隔（秒）。デフォルトは1.0秒
            use_dynamic: Trueの場合、時間経過で値が変化する動的モックを使用
        """
        self.xshut_pins = xshut_pins
        self.i2c_addresses = i2c_addresses
        self._front_distance = front_distance
        self._left_distance = left_distance
        self._right_distance = right_distance
        self._use_random = use_random
        self._random_range = random_range
        self._is_initialized = False
        self._log_interval_sec = log_interval_sec
        self._last_log_time = 0.0
        self._read_count = 0
        self._use_dynamic = use_dynamic
        self._start_time = time.time()
        self._base_left = left_distance if left_distance is not None else 200
        self._base_front = front_distance if front_distance is not None else 500
        self._base_right = right_distance if right_distance is not None else 300
    
    def _initialize_hardware(self) -> None:
        """ハードウェアを初期化（モック：ログ出力のみ）"""
        if self._is_initialized:
            return
        
        print("[MOCK] TOF sensors initialized (mock mode)")
        print(f"[MOCK] XSHUT pins: {self.xshut_pins}")
        print(f"[MOCK] I2C addresses: {[hex(addr) for addr in self.i2c_addresses]}")
        self._is_initialized = True
    
    def _get_random_distance(self) -> int:
        """ランダムな距離を生成（mm）"""
        return random.randint(self._random_range[0], self._random_range[1])
    
    def _get_front_distance(self) -> int:
        """前のセンサーの距離を取得（mm）"""
        if self._use_random:
            return self._get_random_distance()
        if self._use_dynamic:
            # 時間経過で値が変わる（シミュレーション用）
            elapsed = time.time() - self._start_time
            # 周期的に変化させる（例：500mm ± 50mm）
            variation = int(50 * (1 + 0.5 * (elapsed % 4.0) / 4.0))
            return self._base_front + variation - 25
        if self._front_distance is None:
            return self._get_random_distance()
        return self._front_distance
    
    def _get_left_distance(self) -> int:
        """左のセンサーの距離を取得（mm）"""
        if self._use_random:
            return self._get_random_distance()
        if self._use_dynamic:
            # 時間経過で値が変わる（壁沿い走行のシミュレーション）
            elapsed = time.time() - self._start_time
            # 目標距離200mmの周りで変化（180mm～220mm）
            # サイン波で滑らかに変化
            variation = int(20 * math.sin(elapsed * 0.5))  # 約12.5秒周期
            return self._base_left + variation
        if self._left_distance is None:
            return self._get_random_distance()
        return self._left_distance
    
    def _get_right_distance(self) -> int:
        """右のセンサーの距離を取得（mm）"""
        if self._use_random:
            return self._get_random_distance()
        if self._use_dynamic:
            # 時間経過で値が変わる（シミュレーション用）
            elapsed = time.time() - self._start_time
            # 周期的に変化させる（例：300mm ± 30mm）
            variation = int(30 * math.cos(elapsed * 0.3))
            return self._base_right + variation
        if self._right_distance is None:
            return self._get_random_distance()
        return self._right_distance
    
    def read_tof_readings(self) -> TOFReadings:
        """
        3つのTOFセンサーから距離を読み取る（モック、TOFReadings形式）
        
        Returns:
            TOFReadings: 前、左、右の距離（mm）
        """
        if not self._is_initialized:
            self._initialize_hardware()
        
        front = self._get_front_distance()
        left = self._get_left_distance()
        right = self._get_right_distance()
        
        readings = TOFReadings(front=front, left=left, right=right)
        
        # ログ出力頻度を制限（一定時間ごとに出力）
        current_time = time.time()
        self._read_count += 1
        if current_time - self._last_log_time >= self._log_interval_sec:
            elapsed = current_time - self._start_time
            print(f"[MOCK] TOF readings (#{self._read_count}, t={elapsed:.1f}s): 前={front}mm, 左={left}mm, 右={right}mm")
            self._last_log_time = current_time
        
        return readings
    
    def read(self) -> DistanceData:
        """
        3つのTOFセンサーから距離を読み取る（モック、DistanceData形式）
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
        
        distance = self._get_front_distance()
        
        # ログ出力頻度を制限
        current_time = time.time()
        if current_time - self._last_log_time >= self._log_interval_sec:
            print(f"[MOCK] Front TOF: {distance}mm")
            self._last_log_time = current_time
        
        return distance
    
    def read_left(self) -> int:
        """左のセンサーから距離を読み取る（mm）"""
        if not self._is_initialized:
            self._initialize_hardware()
        
        distance = self._get_left_distance()
        
        # ログ出力頻度を制限
        current_time = time.time()
        if current_time - self._last_log_time >= self._log_interval_sec:
            print(f"[MOCK] Left TOF: {distance}mm")
            self._last_log_time = current_time
        
        return distance
    
    def read_right(self) -> int:
        """右のセンサーから距離を読み取る（mm）"""
        if not self._is_initialized:
            self._initialize_hardware()
        
        distance = self._get_right_distance()
        
        # ログ出力頻度を制限
        current_time = time.time()
        if current_time - self._last_log_time >= self._log_interval_sec:
            print(f"[MOCK] Right TOF: {distance}mm")
            self._last_log_time = current_time
        
        return distance
    
    def close(self) -> None:
        """リソースを解放（モック：何もしない）"""
        print("[MOCK] TOF sensors closed")
        self._is_initialized = False
