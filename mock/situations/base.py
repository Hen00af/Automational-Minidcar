"""
Situation基底クラスモジュール（Strategy Pattern）

異なる状況（前方に壁がある、カーブがあるなど）を切り替えてテストできるようにする。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
import math
import time

from act.domain.distance import DistanceData
from mock.config.constants import (
    DEFAULT_LEFT_DISTANCE_MM,
    DEFAULT_FRONT_DISTANCE_MM,
    DEFAULT_RIGHT_DISTANCE_MM,
)


class BaseSituation(ABC):
    """
    状況（Situation）の基底クラス
    
    Strategyパターンを使用して、異なる状況を切り替えてテストできるようにする。
    各Situationは経過時間に基づいて距離データを生成する。
    
    Attributes:
        _start_time: 開始時刻（秒）
    """
    
    def __init__(self):
        """
        初期化
        
        開始時刻を記録する。
        """
        self._start_time = time.time()
    
    @abstractmethod
    def get_distances(self, time_elapsed: float) -> DistanceData:
        """
        経過時間に基づいて距離データを取得
        
        Args:
            time_elapsed: 開始からの経過時間（秒）
        
        Returns:
            DistanceData: 距離データ（前、左、右）
        
        Raises:
            NotImplementedError: サブクラスで実装されていない場合
        """
        raise NotImplementedError("Subclasses must implement get_distances")
    
    def get_elapsed_time(self) -> float:
        """
        開始からの経過時間を取得
        
        Returns:
            経過時間（秒）
        """
        return time.time() - self._start_time
    
    def reset(self) -> None:
        """
        開始時刻をリセット
        
        テストやシミュレーションの再開時に使用する。
        """
        self._start_time = time.time()


class DefaultSituation(BaseSituation):
    """
    デフォルトの状況（壁沿い走行シミュレーション）
    
    左側に壁がある想定で、壁沿い走行をシミュレートする。
    時間経過で値が変化する動的なシミュレーション。
    
    Attributes:
        _base_left: 左側の基準距離（mm）
        _base_front: 前方の基準距離（mm）
        _base_right: 右側の基準距離（mm）
    """
    
    # シミュレーションのパラメータ
    LEFT_VARIATION_AMPLITUDE: float = 20.0  # 左側の変動幅（mm）
    LEFT_VARIATION_FREQUENCY: float = 0.5    # 左側の変動周波数（Hz）
    FRONT_VARIATION_AMPLITUDE: float = 50.0  # 前方の変動幅（mm）
    FRONT_VARIATION_PERIOD: float = 4.0      # 前方の変動周期（秒）
    RIGHT_VARIATION_AMPLITUDE: float = 30.0 # 右側の変動幅（mm）
    RIGHT_VARIATION_FREQUENCY: float = 0.3   # 右側の変動周波数（Hz）
    
    def __init__(
        self,
        left_distance: float = DEFAULT_LEFT_DISTANCE_MM,
        front_distance: float = DEFAULT_FRONT_DISTANCE_MM,
        right_distance: float = DEFAULT_RIGHT_DISTANCE_MM
    ):
        """
        初期化
        
        Args:
            left_distance: 左側の基準距離（mm）
            front_distance: 前方の基準距離（mm）
            right_distance: 右側の基準距離（mm）
        """
        super().__init__()
        self._base_left = left_distance
        self._base_front = front_distance
        self._base_right = right_distance
    
    def get_distances(self, time_elapsed: float) -> DistanceData:
        """
        経過時間に基づいて距離データを取得
        
        時間経過で値が変化する動的なシミュレーション。
        
        Args:
            time_elapsed: 開始からの経過時間（秒）
        
        Returns:
            DistanceData: 距離データ
        """
        # 左側：目標距離の周りで変化（壁沿い走行のシミュレーション）
        left_variation = (
            self.LEFT_VARIATION_AMPLITUDE *
            math.sin(time_elapsed * self.LEFT_VARIATION_FREQUENCY * 2 * math.pi)
        )
        left = self._base_left + left_variation
        
        # 前方：周期的に変化
        front_variation = (
            self.FRONT_VARIATION_AMPLITUDE *
            (1 + 0.5 * (time_elapsed % self.FRONT_VARIATION_PERIOD) / self.FRONT_VARIATION_PERIOD) -
            self.FRONT_VARIATION_AMPLITUDE / 2
        )
        front = self._base_front + front_variation
        
        # 右側：周期的に変化
        right_variation = (
            self.RIGHT_VARIATION_AMPLITUDE *
            math.cos(time_elapsed * self.RIGHT_VARIATION_FREQUENCY * 2 * math.pi)
        )
        right = self._base_right + right_variation
        
        return DistanceData(
            front_mm=front,
            left_mm=left,
            right_mm=right,
            timestamp=time.time()
        )
