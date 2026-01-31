# --------------------------------
# decision/wall_follow.py
# 左壁沿い走行のPD制御による判断実装
# --------------------------------
from __future__ import annotations

import time

from ..domain.command import Command, DriveMode
from ..domain.features import WallFeatures
from ..config import decision
from .differential import DifferentialController


class WallFollowDecision:
    """
    左壁沿い走行のPD制御による判断モジュール

    左壁との距離誤差を元に、ステアリングと速度を決定します。
    P制御（比例制御）とD制御（微分制御）を組み合わせたPD制御を使用します。
    """

    def __init__(
        self,
        kp: float = decision.wall_follow.KP,
        kd: float = decision.wall_follow.KD,
        differential_smoothing_factor: float = decision.wall_follow.DIFFERENTIAL_SMOOTHING_FACTOR,
        base_speed: float = decision.wall_follow.BASE_SPEED,
        max_steering: float = decision.wall_follow.MAX_STEERING,
        front_blocked_speed: float = decision.wall_follow.FRONT_BLOCKED_SPEED,
        front_steer_gain: float = decision.wall_follow.FRONT_STEER_GAIN,
        front_threshold_mm: float = decision.wall_follow.FRONT_THRESHOLD_MM,
        corner_left_speed: float = decision.wall_follow.CORNER_LEFT_SPEED,
        corner_left_steer_gain: float = decision.wall_follow.CORNER_LEFT_STEER_GAIN,
        corner_left_threshold_mm: float = decision.wall_follow.CORNER_LEFT_THRESHOLD_MM,
    ):
        self.kp = kp
        self.base_speed = base_speed
        self.max_steering = max_steering
        self.front_blocked_speed = front_blocked_speed
        self.front_steer_gain = front_steer_gain
        self.front_threshold_mm = front_threshold_mm
        self.corner_left_speed = corner_left_speed
        self.corner_left_steer_gain = corner_left_steer_gain
        self.corner_left_threshold_mm = corner_left_threshold_mm

        # D制御器を初期化
        self._differential_controller = DifferentialController(
            kd=kd, smoothing_factor=differential_smoothing_factor
        )

        # frame_idカウンター
        self._frame_id = 0

    def decide(self, features: WallFeatures) -> Command:
        """
        特徴量から制御コマンドを決定

        Args:
            features: 壁の特徴量

        Returns:
            Command: 制御コマンド
        """
        current_time = time.time()
        self._frame_id += 1

        # 1. 左コーナー（左に壁がない）の場合：左折（比例制御）
        #    steer = clamp(Kc * (left_front - threshold), 0, 1)
        if not features.is_left_wall:
            steer = self.corner_left_steer_gain * (
                features.left_front_distance_mm - self.corner_left_threshold_mm
            )
            steer = max(0.0, min(steer, 1.0))
            return Command(
                frame_id=self._frame_id,
                t_capture_sec=current_time,
                steer=steer,
                throttle=self.corner_left_speed,
                mode=DriveMode.SLOW,
                reason="corner_left",
            )

        # 2. 前方に壁がある場合：右折（比例制御）
        #    steer = clamp(-Kf * (threshold - front), -1, 0)
        if features.is_front_blocked:
            steer = -self.front_steer_gain * (
                self.front_threshold_mm - features.front_distance_mm
            )
            steer = max(-1.0, min(steer, 0.0))
            return Command(
                frame_id=self._frame_id,
                t_capture_sec=current_time,
                steer=steer,
                throttle=self.front_blocked_speed,
                mode=DriveMode.STOP
                if self.front_blocked_speed == 0.0
                else DriveMode.SLOW,
                reason="front_blocked",
            )

        # 3. 通常の壁沿い制御（PD制御）
        error = features.error_from_target

        # P制御: 誤差に比例してステアリングを計算
        # 誤差が正（離れすぎ）-> 左に寄る必要がある -> steering を正の値にする
        # 誤差が負（近すぎ）-> 右に寄る必要がある -> steering を負の値にする
        p_term = error * self.kp

        # D制御: 誤差の変化率を計算して過剰な応答を抑制
        d_term = self._differential_controller.update(error, current_time)

        # PD制御: P項とD項を組み合わせ
        steering = p_term + d_term

        # ステアリングを -1.0 〜 1.0 の範囲にクランプ
        steering = max(min(steering, self.max_steering), -self.max_steering)

        return Command(
            frame_id=self._frame_id,
            t_capture_sec=current_time,
            steer=steering,
            throttle=self.base_speed,
            mode=DriveMode.RUN,
            reason="wall_follow",
        )
