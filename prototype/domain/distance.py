# --------------------------------
# domain/distance.py
# 距離センサーのデータ型定義
# --------------------------------
from __future__ import annotations

from dataclasses import dataclass
import time


@dataclass
class DistanceData:
    """
    TOFセンサーから取得した距離データ
    """
    front_mm: float  # 前方距離 (mm)
    left_mm: float   # 左方距離 (mm)
    left_front_mm: float  # 左前方距離 (mm)
    timestamp: float  # タイムスタンプ（秒）

    @classmethod
    def from_tof_readings(cls, readings: "TOFReadings", timestamp: float | None = None) -> DistanceData:
        """
        TOFReadingsからDistanceDataを作成
        
        Args:
            readings: TOFReadingsオブジェクト
            timestamp: タイムスタンプ（Noneの場合は現在時刻）
        """
        if timestamp is None:
            timestamp = time.time()
        return cls(
            front_mm=float(readings.front),
            left_mm=float(readings.left),
            left_front_mm=float(readings.left_front),
            timestamp=timestamp
        )
