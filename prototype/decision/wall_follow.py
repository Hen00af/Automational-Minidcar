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
        steer_near_distance_mm: float = decision.wall_follow.STEER_NEAR_DISTANCE_MM,
        steer_far_distance_mm: float = decision.wall_follow.STEER_FAR_DISTANCE_MM,
        front_blocked_speed: float = decision.wall_follow.FRONT_BLOCKED_SPEED,
        front_blocked_near_steering: float = decision.wall_follow.FRONT_BLOCKED_NEAR_STEERING,
        front_blocked_far_steering: float = decision.wall_follow.FRONT_BLOCKED_FAR_STEERING,
        corner_left_speed: float = decision.wall_follow.CORNER_LEFT_SPEED,
        corner_left_near_steering: float = decision.wall_follow.CORNER_LEFT_NEAR_STEERING,
        corner_left_far_steering: float = decision.wall_follow.CORNER_LEFT_FAR_STEERING,
        speed_reduction_factor: float = decision.wall_follow.SPEED_REDUCTION_FACTOR,
        max_steering_rate: float = decision.wall_follow.MAX_STEERING_RATE,
    ):
        """
        初期化

        Args:
            kp: P制御の比例ゲイン。デフォルトは設定ファイルの値
            kd: D制御の微分ゲイン。デフォルトは設定ファイルの値（0.0で無効）
            differential_smoothing_factor: 微分値の平滑化係数 [0.0, 1.0]。デフォルトは設定ファイルの値
            base_speed: 通常走行時の基本速度 [0.0, 1.0]。デフォルトは設定ファイルの値
            max_steering: ステアリングの最大値（絶対値）。デフォルトは設定ファイルの値
            steer_near_distance_mm: 比例制御の近距離閾値（mm）。デフォルトは設定ファイルの値
            steer_far_distance_mm: 比例制御の遠距離閾値（mm）。デフォルトは設定ファイルの値
            front_blocked_speed: 前方に壁がある場合の速度。デフォルトは設定ファイルの値
            front_blocked_near_steering: 前方壁が近い時のステアリング（右折用）。デフォルトは設定ファイルの値
            front_blocked_far_steering: 前方壁が遠い時のステアリング（右折用）。デフォルトは設定ファイルの値
            corner_left_speed: 左コーナー時の速度。デフォルトは設定ファイルの値
            corner_left_near_steering: 前方壁が近い時の左折ステアリング。デフォルトは設定ファイルの値
            corner_left_far_steering: 前方壁が遠い時の左折ステアリング。デフォルトは設定ファイルの値
            speed_reduction_factor: ステアリング角に応じた減速係数 [0.0, 1.0]。デフォルトは設定ファイルの値
            max_steering_rate: 1秒あたりのステアリング最大変化量。0.0で無制限。デフォルトは設定ファイルの値
        """
        self.kp = kp
        self.base_speed = base_speed
        self.max_steering = max_steering
        self.steer_near_distance_mm = steer_near_distance_mm
        self.steer_far_distance_mm = steer_far_distance_mm
        self.front_blocked_speed = front_blocked_speed
        self.front_blocked_near_steering = front_blocked_near_steering
        self.front_blocked_far_steering = front_blocked_far_steering
        self.corner_left_speed = corner_left_speed
        self.corner_left_near_steering = corner_left_near_steering
        self.corner_left_far_steering = corner_left_far_steering
        self.speed_reduction_factor = speed_reduction_factor
        self.max_steering_rate = max_steering_rate

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
            features: 壁の特徴量

        Returns:
            Command: 制御コマンド
        """
        current_time = time.time()
        self._frame_id += 1

        # 1. 左コーナー（左に壁がない）の場合：左折
        if not features.is_left_wall:
            target_steer = self._proportional_steering(
                features.front_distance_mm,
                self.corner_left_near_steering,
                self.corner_left_far_steering,
            )
            steer = self._apply_rate_limit(target_steer, current_time)
            throttle = self._apply_curve_deceleration(
                self.corner_left_speed, steer
            )
            return Command(
                frame_id=self._frame_id,
                t_capture_sec=current_time,
                steer=steer,
                throttle=throttle,
                mode=DriveMode.SLOW,
                reason="corner_left",
            )

        # 2. 前方に壁がある場合：停止または右折
        if features.is_front_blocked:
            target_steer = self._proportional_steering(
                features.front_distance_mm,
                self.front_blocked_near_steering,
                self.front_blocked_far_steering,
            )
            steer = self._apply_rate_limit(target_steer, current_time)
            throttle = self._apply_curve_deceleration(
                self.front_blocked_speed, steer
            )
            return Command(
                frame_id=self._frame_id,
                t_capture_sec=current_time,
                steer=steer,
                throttle=throttle,
                mode=DriveMode.STOP
                if throttle == 0.0
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

        steering = self._apply_rate_limit(steering, current_time)
        throttle = self._apply_curve_deceleration(self.base_speed, steering)

        return Command(
            frame_id=self._frame_id,
            t_capture_sec=current_time,
            steer=steering,
            throttle=throttle,
            mode=DriveMode.RUN,
            reason="wall_follow",
        )

    def _proportional_steering(
        self, front_distance_mm: float, near_steering: float, far_steering: float
    ) -> float:
        """
        前方壁との距離に応じてステアリング値を線形補間する。

        近距離（steer_near_distance_mm以下）では near_steering、
        遠距離（steer_far_distance_mm以上）では far_steering を返す。

        Args:
            front_distance_mm: 前方壁との距離（mm）
            near_steering: 近距離時のステアリング値
            far_steering: 遠距離時のステアリング値

        Returns:
            補間されたステアリング値
        """
        near = self.steer_near_distance_mm
        far = self.steer_far_distance_mm
        t = (front_distance_mm - near) / (far - near)
        t = max(0.0, min(1.0, t))
        return near_steering + t * (far_steering - near_steering)

    def _apply_rate_limit(self, target_steer: float, current_time: float) -> float:
        """
        ステアリングの変化量を制限する（レートリミッター）。

        1フレームあたりの変化量を max_steering_rate * dt 以内に抑える。

        Args:
            target_steer: 目標ステアリング値 [-1.0, 1.0]
            current_time: 現在時刻（秒）

        Returns:
            レートリミット適用後のステアリング値
        """
        if self.max_steering_rate <= 0.0 or self._prev_steer_time is None:
            self._prev_steer = target_steer
            self._prev_steer_time = current_time
            return target_steer

        dt = current_time - self._prev_steer_time
        if dt <= 0.0:
            return self._prev_steer

        max_delta = self.max_steering_rate * dt
        delta = target_steer - self._prev_steer
        delta = max(min(delta, max_delta), -max_delta)

        result = self._prev_steer + delta
        self._prev_steer = result
        self._prev_steer_time = current_time
        return result

    def _apply_curve_deceleration(self, base_speed: float, steering: float) -> float:
        """
        ステアリング角に応じて速度を減速する。

        speed = base_speed * (1.0 - speed_reduction_factor * |steering|)

        Args:
            base_speed: 減速前の基本速度
            steering: ステアリング値 [-1.0, 1.0]

        Returns:
            減速後の速度 [0.0, base_speed]
        """
        return base_speed * (1.0 - self.speed_reduction_factor * abs(steering))
