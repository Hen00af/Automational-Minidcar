"""
モックセンサー実装
"""
from __future__ import annotations

import time
from typing import Optional

from mock.situations.base import BaseSituation
from mock.config.constants import DEFAULT_LOG_INTERVAL_SEC
from mock.core.utils import get_logger
from act.domain.distance import DistanceData
from act.interfaces.protocols import DistanceSensorModule


class MockSensor(DistanceSensorModule):
    """
    モックセンサークラス
    
    Situation（状況）に基づいて距離データを返す。
    Dependency Injectionパターンを使用して、Situationを外部から注入する。
    
    Attributes:
        situation: 状況オブジェクト（Dependency Injection）
        _logger: ロガーインスタンス
        _read_count: 読み取り回数
        _last_log_time: 最後のログ出力時刻
        _log_interval_sec: ログ出力間隔（秒）
    """
    
    def __init__(
        self,
        situation: BaseSituation,
        verbose: bool = False,
        log_interval_sec: float = DEFAULT_LOG_INTERVAL_SEC
    ):
        """
        初期化
        
        Args:
            situation: 状況オブジェクト（Dependency Injection）
            verbose: Trueの場合、詳細ログを出力する。デフォルトはFalse
            log_interval_sec: ログ出力間隔（秒）
        
        Raises:
            ValueError: situationがNoneの場合
        """
        if situation is None:
            raise ValueError("situation must not be None")
        
        self.situation = situation
        self._verbose = verbose
        self._read_count = 0
        self._last_log_time = 0.0
        self._log_interval_sec = log_interval_sec
        self._logger = get_logger("mock.sensor")
    
    def read(self) -> DistanceData:
        """
        3つのTOFセンサーから距離を読み取る（DistanceData形式）
        
        DistanceSensorModuleプロトコルに適合。
        Situationから経過時間に基づいた距離データを取得する。
        
        Returns:
            DistanceData: 前、左、右の距離データ（タイムスタンプ付き）
        """
        elapsed_time = self.situation.get_elapsed_time()
        distance_data = self.situation.get_distances(elapsed_time)
        
        self._read_count += 1
        
        # ログ出力頻度を制限（一定時間ごとに出力）
        if self._verbose:
            current_time = time.time()
            if current_time - self._last_log_time >= self._log_interval_sec:
                self._logger.info(
                    "Sensor reading (#%d, t=%.1fs): 前=%.0fmm, 左=%.0fmm, 右=%.0fmm",
                    self._read_count,
                    elapsed_time,
                    distance_data.front_mm,
                    distance_data.left_mm,
                    distance_data.right_mm
                )
                self._last_log_time = current_time
        
        return distance_data
    
    def close(self) -> None:
        """
        リソースを解放
        
        モック実装では実際のリソースは使用していないが、
        インターフェースの一貫性のために実装されている。
        """
        if self._verbose:
            self._logger.info("Sensor closed")
