# --------------------------------
# perception/wall_position.py
# 距離データから回廊内の位置関係を特定する知覚モジュール実装
# --------------------------------
from __future__ import annotations

from ..domain.distance import DistanceData
from ..domain.features import WallFeatures
from ..config import perception


class CorridorPerception:
    """
    距離データから回廊内の位置関係を特定する知覚モジュール

    正面・左斜め前・右斜め前の3センサーを使用して、以下の特徴量を抽出します：
    - 左右バランス誤差（回廊中央からのズレ）
    - 前方の障害物判定
    - 各方向の距離情報（速度制御・回避方向判断用）
    - コーナー接近の予測（左右の距離差から判定）
    """

    def __init__(
        self,
        front_blocked_threshold_mm: float = perception.corridor.FRONT_BLOCKED_THRESHOLD_MM,
        front_slow_threshold_mm: float = perception.corridor.FRONT_SLOW_THRESHOLD_MM,
        wall_detection_threshold_mm: float = perception.corridor.WALL_DETECTION_THRESHOLD_MM,
        corner_imbalance_ratio: float = perception.corridor.CORNER_IMBALANCE_RATIO,
        corner_near_wall_threshold_mm: float = perception.corridor.CORNER_NEAR_WALL_THRESHOLD_MM,
    ):
        """
        初期化

        Args:
            front_blocked_threshold_mm: 前方が障害物と判定する距離の閾値（mm）。デフォルトは設定ファイルの値
            front_slow_threshold_mm: 前方減速を開始する距離の閾値（mm）。デフォルトは設定ファイルの値
            wall_detection_threshold_mm: 壁を検知する最大距離（mm）。デフォルトは設定ファイルの値
            corner_imbalance_ratio: コーナー予測を発動する左右距離比の閾値。デフォルトは設定ファイルの値
            corner_near_wall_threshold_mm: コーナー予測の前提条件となる近壁距離閾値（mm）。デフォルトは設定ファイルの値
        """
        self.front_blocked_threshold_mm = front_blocked_threshold_mm
        self.front_slow_threshold_mm = front_slow_threshold_mm
        self.wall_detection_threshold_mm = wall_detection_threshold_mm
        self.corner_imbalance_ratio = corner_imbalance_ratio
        self.corner_near_wall_threshold_mm = corner_near_wall_threshold_mm

    def analyze(self, data: DistanceData) -> WallFeatures:
        """
        距離データから特徴量を抽出

        Args:
            data: 距離データ

        Returns:
            WallFeatures: 抽出した特徴量
        """
        # 左右バランス誤差を計算
        # left_front_mm - right_front_mm:
        #   正の値 → 左が遠い（右寄り）→ 左に寄る必要がある → steering を正の値にする
        #   負の値 → 右が遠い（左寄り）→ 右に寄る必要がある → steering を負の値にする
        left_front = min(data.left_front_mm, self.wall_detection_threshold_mm)
        right_front = min(data.right_front_mm, self.wall_detection_threshold_mm)
        left_right_error = left_front - right_front

        # 前方の障害物判定（閾値以内なら障害物あり）
        front_blocked = data.front_mm < self.front_blocked_threshold_mm

        # コーナー予測: 左右斜めセンサーの比率からコーナー接近を判定
        is_corner_approaching = False
        corner_severity = 0.0
        near_wall = min(left_front, right_front)
        far_wall = max(left_front, right_front)

        if near_wall < self.corner_near_wall_threshold_mm and near_wall > 0:
            ratio = far_wall / near_wall
            if ratio >= self.corner_imbalance_ratio:
                is_corner_approaching = True
                # severity: 比率が大きいほど深いコーナー（0.0〜1.0にクランプ）
                corner_severity = min(
                    (ratio - self.corner_imbalance_ratio) / self.corner_imbalance_ratio,
                    1.0,
                )

        return WallFeatures(
            left_right_error=left_right_error,
            is_front_blocked=front_blocked,
            front_distance_mm=data.front_mm,
            left_front_mm=data.left_front_mm,
            right_front_mm=data.right_front_mm,
            is_corner_approaching=is_corner_approaching,
            corner_severity=corner_severity,
        )
