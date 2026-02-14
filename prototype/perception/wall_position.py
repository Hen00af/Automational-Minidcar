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
    """

    def __init__(
        self,
        front_blocked_threshold_mm: float = perception.corridor.FRONT_BLOCKED_THRESHOLD_MM,
        front_slow_threshold_mm: float = perception.corridor.FRONT_SLOW_THRESHOLD_MM,
        wall_detection_threshold_mm: float = perception.corridor.WALL_DETECTION_THRESHOLD_MM,
        fork_front_threshold_mm: float = perception.corridor.FORK_FRONT_THRESHOLD_MM,
        fork_side_open_threshold_mm: float = perception.corridor.FORK_SIDE_OPEN_THRESHOLD_MM,
    ):
        """
        初期化

        Args:
            front_blocked_threshold_mm: 前方が障害物と判定する距離の閾値（mm）。デフォルトは設定ファイルの値
            front_slow_threshold_mm: 前方減速を開始する距離の閾値（mm）。デフォルトは設定ファイルの値
            wall_detection_threshold_mm: 壁を検知する最大距離（mm）。デフォルトは設定ファイルの値
            fork_front_threshold_mm: Y字分岐で正面が壁を検知する距離の閾値（mm）
            fork_side_open_threshold_mm: Y字分岐で左右が「開けている」と判定する距離の閾値（mm）
        """
        self.front_blocked_threshold_mm = front_blocked_threshold_mm
        self.front_slow_threshold_mm = front_slow_threshold_mm
        self.wall_detection_threshold_mm = wall_detection_threshold_mm
        self.fork_front_threshold_mm = fork_front_threshold_mm
        self.fork_side_open_threshold_mm = fork_side_open_threshold_mm

    def analyze(self, data: DistanceData) -> WallFeatures:
        """
        距離データから特徴量を抽出

        Args:
            data: 距離データ

        Returns:
            WallFeatures: 抽出した特徴量
        """
        # 左右バランス誤差を計算（回廊幅で正規化して -1.0〜+1.0 の範囲に収める）
        # (left - right) / (left + right):
        #   正の値 → 左が遠い（右寄り）→ 左に寄る必要がある → steering を正の値にする
        #   負の値 → 右が遠い（左寄り）→ 右に寄る必要がある → steering を負の値にする
        left_front = min(data.left_front_mm, self.wall_detection_threshold_mm)
        right_front = min(data.right_front_mm, self.wall_detection_threshold_mm)
        corridor_width = left_front + right_front
        if corridor_width > 0:
            left_right_error = (left_front - right_front) / corridor_width
        else:
            left_right_error = 0.0

        # 前方の障害物判定（閾値以内なら障害物あり）
        front_blocked = data.front_mm < self.front_blocked_threshold_mm

        # Y字分岐の検知
        # 条件: 正面が中距離で壁を検知 AND 左右の両方が開けている
        # → 分岐の島（中央の壁）が正面にあり、左右に通路が見えている状態
        fork_detected = (
            data.front_mm < self.fork_front_threshold_mm
            and data.left_front_mm > self.fork_side_open_threshold_mm
            and data.right_front_mm > self.fork_side_open_threshold_mm
        )

        return WallFeatures(
            left_right_error=left_right_error,
            is_front_blocked=front_blocked,
            is_fork_detected=fork_detected,
            front_distance_mm=data.front_mm,
            left_front_mm=data.left_front_mm,
            right_front_mm=data.right_front_mm,
        )
