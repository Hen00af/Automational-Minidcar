# --------------------------------
# perception/wall_position.py
# 距離データから壁の位置関係を特定する知覚モジュール実装
# --------------------------------
from __future__ import annotations

from ..domain.distance import DistanceData
from ..domain.features import WallFeatures
from ..config import perception


class WallPositionPerception:
    """
    距離データから壁の位置関係を特定する知覚モジュール
    
    左壁沿い走行（左手法）を前提として、以下の特徴量を抽出します：
    - 左壁との距離誤差（目標距離からのズレ）
    - 前方の壁判定
    - 左側のコーナー判定
    """
    
    def __init__(
        self,
        target_distance_mm: float = perception.wall_position.TARGET_DISTANCE_MM,
        front_blocked_threshold_mm: float = perception.wall_position.FRONT_BLOCKED_THRESHOLD_MM,
        corner_left_threshold_mm: float = perception.wall_position.CORNER_LEFT_THRESHOLD_MM
    ):
        """
        初期化
        
        Args:
            target_distance_mm: 左壁との目標距離（mm）。デフォルトは設定ファイルの値
            front_blocked_threshold_mm: 前方が壁と判定する距離の閾値（mm）。デフォルトは設定ファイルの値
            corner_left_threshold_mm: 左側がコーナー（壁がない）と判定する距離の閾値（mm）。デフォルトは設定ファイルの値
        """
        self.target_distance_mm = target_distance_mm
        self.front_blocked_threshold_mm = front_blocked_threshold_mm
        self.corner_left_threshold_mm = corner_left_threshold_mm
    
    def analyze(self, data: DistanceData) -> WallFeatures:
        """
        距離データから特徴量を抽出
        
        Args:
            data: 距離データ
            
        Returns:
            WallFeatures: 抽出した特徴量
        """
        # 左壁との距離誤差（P制御の入力値になる）
        # 正の値：壁から離れすぎている（左に寄る必要がある）
        # 負の値：壁に近すぎる（右に寄る必要がある）
        left_error = data.left_mm - self.target_distance_mm
        left_front_error = data.left_front_mm - self.target_distance_mm
        error = (left_error + left_front_error) / 2.0

        # 前方の壁判定（閾値以内なら壁あり）
        front_blocked = (
            data.front_mm < self.front_blocked_threshold_mm
            or data.left_front_mm < self.front_blocked_threshold_mm
        )

        # 左側のコーナー判定（距離が閾値以上なら壁がない）
        is_corner_left = (
            data.left_mm > self.corner_left_threshold_mm
            and data.left_front_mm > self.corner_left_threshold_mm
        )
        
        return WallFeatures(
            error_from_target=error,
            is_front_blocked=front_blocked,
            is_corner_left=is_corner_left
        )
