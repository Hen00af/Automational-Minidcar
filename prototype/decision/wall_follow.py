# --------------------------------
# decision/wall_follow.py
# 回廊中央走行のPD制御による判断実装
# --------------------------------
from __future__ import annotations

import time

from ..domain.command import Command, DriveMode
from ..domain.features import WallFeatures
from ..config import decision, perception
from .differential import DifferentialController


class CorridorDecision:
    """
    回廊中央走行のPD制御による判断モジュール

    左右のセンサー差分を元に、ステアリングと速度を決定します。
    P制御（比例制御）とD制御（微分制御）を組み合わせたPD制御を使用します。
    """

    def __init__(
        self,
        kp: float = decision.corridor.KP,
        kd: float = decision.corridor.KD,
        differential_smoothing_factor: float = decision.corridor.DIFFERENTIAL_SMOOTHING_FACTOR,
        base_speed: float = decision.corridor.BASE_SPEED,
        high_speed: float = decision.corridor.HIGH_SPEED,
        max_steering: float = decision.corridor.MAX_STEERING,
        front_blocked_speed: float = decision.corridor.FRONT_BLOCKED_SPEED,
        front_blocked_steering: float = decision.corridor.FRONT_BLOCKED_STEERING,
        front_slow_threshold_mm: float = perception.corridor.FRONT_SLOW_THRESHOLD_MM,
        corner_approach_speed: float = decision.corridor.CORNER_APPROACH_SPEED,
    ):
        """
        初期化

        Args:
            kp: P制御の比例ゲイン。デフォルトは設定ファイルの値
            kd: D制御の微分ゲイン。デフォルトは設定ファイルの値（0.0で無効）
            differential_smoothing_factor: 微分値の平滑化係数 [0.0, 1.0]。デフォルトは設定ファイルの値
            base_speed: 通常走行時の基本速度 [0.0, 1.0]。デフォルトは設定ファイルの値
            high_speed: 前方が開けている場合の高速 [0.0, 1.0]。デフォルトは設定ファイルの値
            max_steering: ステアリングの最大値（絶対値）。デフォルトは設定ファイルの値
            front_blocked_speed: 前方に障害物がある場合の速度。デフォルトは設定ファイルの値
            front_blocked_steering: 前方障害物時のデフォルトステアリング。デフォルトは設定ファイルの値
            front_slow_threshold_mm: 前方減速開始の閾値（mm）。デフォルトは設定ファイルの値
            corner_approach_speed: コーナー接近時の減速目標速度。デフォルトは設定ファイルの値
        """
        self.kp = kp
        self.base_speed = base_speed
        self.high_speed = high_speed
        self.max_steering = max_steering
        self.front_blocked_speed = front_blocked_speed
        self.front_blocked_steering = front_blocked_steering
        self.front_slow_threshold_mm = front_slow_threshold_mm
        self.corner_approach_speed = corner_approach_speed

        # D制御器を初期化
        self._differential_controller = DifferentialController(
            kd=kd, smoothing_factor=differential_smoothing_factor
        )

        # frame_idカウンター
        self._frame_id = 0

        # レートリミッター用の前回値
        self._prev_steer: float = 0.0
        self._prev_steer_time: float | None = None

    def decide(self, features: WallFeatures) -> Command:
        """
        特徴量から制御コマンドを決定

        Args:
            features: 回廊走行の特徴量

        Returns:
            Command: 制御コマンド
        """
        current_time = time.time()
        self._frame_id += 1

        # 1. 前方に障害物がある場合：左右の空きを比較して回避方向を決定
        if features.is_front_blocked:
            # 左右のセンサー値を比較し、空いている方に回避
            if features.left_front_mm >= features.right_front_mm:
                # 左の方が空いている → 左に回避（正のステアリング）
                avoid_steering = abs(self.front_blocked_steering)
            else:
                # 右の方が空いている → 右に回避（負のステアリング）
                avoid_steering = -abs(self.front_blocked_steering)

            return Command(
                frame_id=self._frame_id,
                t_capture_sec=current_time,
                steer=avoid_steering,
                throttle=self.front_blocked_speed,
                mode=DriveMode.SLOW,
                reason="front_blocked",
            )

        # 2. 通常の回廊中央走行（PD制御）
        error = features.left_right_error

        # P制御: 左右バランス誤差に比例してステアリングを計算
        # 誤差が正（右寄り）-> 左に寄る必要がある -> steering を正の値にする
        # 誤差が負（左寄り）-> 右に寄る必要がある -> steering を負の値にする
        p_term = error * self.kp

        # D制御: 誤差の変化率を計算して過剰な応答を抑制
        d_term = self._differential_controller.update(error, current_time)

        # PD制御: P項とD項を組み合わせ
        steering = p_term + d_term

        # ステアリングを -max_steering 〜 +max_steering の範囲にクランプ
        steering = max(min(steering, self.max_steering), -self.max_steering)

        # 3. 速度制御: 前方距離に応じて速度を調整
        speed = self._calculate_speed(features.front_distance_mm)

        # 4. コーナー予測減速: コーナー接近時はseverityに応じて減速
        if features.is_corner_approaching:
            corner_speed = (
                self.base_speed
                - (self.base_speed - self.corner_approach_speed)
                * features.corner_severity
            )
            speed = min(speed, corner_speed)

        return Command(
            frame_id=self._frame_id,
            t_capture_sec=current_time,
            steer=steering,
            throttle=speed,
            mode=DriveMode.RUN,
            reason="corner_approach" if features.is_corner_approaching else "corridor_center",
        )

    def _calculate_speed(self, front_distance_mm: float) -> float:
        """
        前方距離に応じた速度を計算

        前方が開けている場合はhigh_speed、障害物が近い場合はbase_speedに減速。
        線形補間で滑らかに遷移。

        Args:
            front_distance_mm: 前方距離（mm）

        Returns:
            float: 速度 [0.0, 1.0]
        """
        if front_distance_mm >= self.front_slow_threshold_mm:
            # 前方がクリア → 高速走行
            return self.high_speed
        else:
            # 前方に障害物が近づいている → 距離に応じて線形に減速
            # front_slow_threshold_mm → high_speed
            # 0mm → base_speed
            ratio = front_distance_mm / self.front_slow_threshold_mm
            return self.base_speed + (self.high_speed - self.base_speed) * ratio
