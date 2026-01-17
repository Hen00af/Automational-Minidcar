# --------------------------------
# decision/wall_follow.py
# 左壁沿い走行のP制御による判断実装
# --------------------------------
from __future__ import annotations

import time

from ..domain.command import Command, DriveMode
from ..domain.features import WallFeatures


class WallFollowDecision:
    """
    左壁沿い走行のP制御による判断モジュール
    
    左壁との距離誤差を元に、ステアリングと速度を決定します。
    純粋なP制御（比例制御）のみを使用します。
    """
    
    def __init__(
        self,
        kp: float = 0.03,
        base_speed: float = 0.5,
        max_steering: float = 1.0,
        front_blocked_speed: float = 0.0,
        front_blocked_steering: float = -0.5,  # 右に曲がる（負の値）
        corner_left_speed: float = 0.3,
        corner_left_steering: float = 0.8,  # 左に曲がる（正の値）
    ):
        """
        初期化
        
        Args:
            kp: P制御の比例ゲイン（デフォルト: 0.03）
            base_speed: 通常走行時の基本速度 [0.0, 1.0]
            max_steering: ステアリングの最大値（絶対値）
            front_blocked_speed: 前方に壁がある場合の速度
            front_blocked_steering: 前方に壁がある場合のステアリング（右折用、負の値）
            corner_left_speed: 左コーナー時の速度
            corner_left_steering: 左コーナー時のステアリング（左折用、正の値）
        """
        self.kp = kp
        self.base_speed = base_speed
        self.max_steering = max_steering
        self.front_blocked_speed = front_blocked_speed
        self.front_blocked_steering = front_blocked_steering
        self.corner_left_speed = corner_left_speed
        self.corner_left_steering = corner_left_steering
        
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
        
        # 1. 前方に壁がある場合：停止または右折
        if features.is_front_blocked:
            return Command(
                frame_id=self._frame_id,
                t_capture_sec=current_time,
                steer=self.front_blocked_steering,  # 右に曲がる（負の値）
                throttle=self.front_blocked_speed,
                mode=DriveMode.STOP if self.front_blocked_speed == 0.0 else DriveMode.SLOW,
                reason="front_blocked"
            )
        
        # 2. 左コーナー（左に壁がない）の場合：左折
        if features.is_corner_left:
            return Command(
                frame_id=self._frame_id,
                t_capture_sec=current_time,
                steer=self.corner_left_steering,  # 左に曲がる（正の値）
                throttle=self.corner_left_speed,
                mode=DriveMode.SLOW,
                reason="corner_left"
            )
        
        # 3. 通常の壁沿い制御（純粋なP制御）
        error = features.error_from_target
        
        # P制御: 誤差に比例してステアリングを計算
        # 誤差が正（離れすぎ）-> 左に寄る必要がある -> steering を正の値にする
        # 誤差が負（近すぎ）-> 右に寄る必要がある -> steering を負の値にする
        steering = error * self.kp
        
        # ステアリングを -1.0 〜 1.0 の範囲にクランプ
        steering = max(min(steering, self.max_steering), -self.max_steering)
        
        return Command(
            frame_id=self._frame_id,
            t_capture_sec=current_time,
            steer=steering,
            throttle=self.base_speed,
            mode=DriveMode.RUN,
            reason="wall_follow"
        )
