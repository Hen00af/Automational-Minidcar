# --------------------------------
# orchestrator/orchestrator.py
# センサー→知覚→判断→駆動のループを統合実行するオーケストレーター
# --------------------------------
from __future__ import annotations

from typing import Optional

from ..interfaces.protocols import DistanceSensorModule, Perception, Decision, Actuation
from ..domain.actuation import Telemetry


class Orchestrator:
    """
    全体をつなぐ役（レベル0単一ループ想定）。
    - 中身（アルゴリズム/ハード）を知らず、I/Fだけで接続する。
    """
    def __init__(
        self,
        sensor: DistanceSensorModule,
        perception: Perception,
        decision: Decision,
        actuation: Actuation
    ):
        """
        初期化
        
        Args:
            sensor: 距離センサーモジュール
            perception: 知覚モジュール
            decision: 判断モジュール
            actuation: 駆動モジュール
        """
        self.sensor = sensor
        self.perception = perception
        self.decision = decision
        self.actuation = actuation
    
    def run_once(self) -> Telemetry:
        """
        1サイクル分の処理（例外処理や安全停止ポリシーは必要に応じて追加）。
        
        Returns:
            Telemetry: 駆動モジュールの適用結果
        """
        # 1. 計測 (Measure)
        distance_data = self.sensor.read()
        
        # 2. 知覚 (Perceive)
        features = self.perception.analyze(distance_data)
        
        # 3. 判断 (Decide)
        command = self.decision.decide(features)
        
        # 4. 実行 (Act)
        telemetry = self.actuation.apply(command)
        return telemetry
    
    def run_loop(self, max_iterations: Optional[int] = None, loop_interval_sec: float = 0.1, log_interval_sec: float = 1.0) -> None:
        """
        連続実行（第1イテレーションは単純に繰り返すだけ）。
        最新優先の高度化（古いフレーム破棄等）は次イテレーションで扱う。
        
        Args:
            max_iterations: 最大実行回数（Noneの場合は無限ループ）
            loop_interval_sec: ループ間隔（秒）。デフォルトは0.1秒（10Hz）
            log_interval_sec: 詳細ログ出力間隔（秒）。デフォルトは1.0秒
        """
        import time
        iteration = 0
        last_log_time = 0.0
        try:
            while max_iterations is None or iteration < max_iterations:
                distance_data = self.sensor.read()
                features = self.perception.analyze(distance_data)
                command = self.decision.decide(features)
                telemetry = self.actuation.apply(command)
                
                # 詳細ログ出力（一定間隔で）
                current_time = time.time()
                iteration += 1
                if current_time - last_log_time >= log_interval_sec:
                    self._log_cycle(iteration, distance_data, features, command, telemetry)
                    last_log_time = current_time
                
                if loop_interval_sec > 0:
                    time.sleep(loop_interval_sec)
        except KeyboardInterrupt:
            print("\n[Orchestrator] Interrupted by user")
            self.emergency_stop("user_interrupt")
        except Exception as e:
            print(f"\n[Orchestrator] Error occurred: {e}")
            self.emergency_stop(f"error: {str(e)}")
    
    def _log_cycle(
        self,
        iteration: int,
        distance_data,
        features,
        command,
        telemetry
    ) -> None:
        """
        1サイクルの詳細情報をログ出力
        
        Args:
            iteration: イテレーション番号
            distance_data: センサーデータ
            features: 知覚結果
            command: 判断結果
            telemetry: 駆動結果
        """
        # 知覚結果
        error_str = f"{features.error_from_target:+.1f}mm"
        front_str = "壁あり" if features.is_front_blocked else "壁なし"
        corner_str = "コーナー" if features.is_corner_left else "通常"
        
        # 判断結果
        mode_str = command.mode.value if hasattr(command.mode, 'value') else str(command.mode)
        reason_str = f"({command.reason})" if command.reason else ""
        
        # 駆動結果
        status_str = telemetry.status.value if hasattr(telemetry.status, 'value') else str(telemetry.status)
        
        print(f"[CYCLE #{iteration}] 知覚: 誤差={error_str}, 前方={front_str}, 左={corner_str} | "
              f"判断: モード={mode_str} {reason_str}, ステア={command.steer:+.2f}, スロットル={command.throttle:.2f} | "
              f"駆動: {status_str}")
    
    def emergency_stop(self, reason: str = "emergency") -> Telemetry:
        """
        上位から明示停止できる入口（設計上の口）。
        
        Args:
            reason: 停止理由
            
        Returns:
            Telemetry: 停止処理の結果
        """
        return self.actuation.stop(reason)
