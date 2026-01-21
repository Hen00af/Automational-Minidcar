# --------------------------------
# orchestrator/orchestrator.py
# センサー→知覚→判断→駆動のループを統合実行するオーケストレーター
# --------------------------------
from __future__ import annotations

import logging
import os
import time
from typing import Optional

from ..interfaces.protocols import DistanceSensorModule, Perception, Decision, Actuation
from ..domain.actuation import Telemetry
from ..domain.distance import DistanceData
from ..domain.features import WallFeatures
from ..domain.command import Command


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
        actuation: Actuation,
        timing_log_path: Optional[str] = "logs/orchestrator_timing.log"
    ):
        """
        初期化
        
        Args:
            sensor: 距離センサーモジュール
            perception: 知覚モジュール
            decision: 判断モジュール
            actuation: 駆動モジュール
            timing_log_path: 計測ログの出力先（Noneで無効）
        """
        self.sensor = sensor
        self.perception = perception
        self.decision = decision
        self.actuation = actuation
        self._loop_index = 0
        self._timing_logger = self._setup_timing_logger(timing_log_path)
        self._timing_start_time = time.time()
        if self._timing_logger:
            self._timing_logger.info("event=run_start t=%.3fs", 0.0)

    def _setup_timing_logger(self, log_path: Optional[str]) -> Optional[logging.Logger]:
        if not log_path:
            return None

        log_dir = os.path.dirname(log_path)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        logger = logging.getLogger(f"orchestrator.timing.{id(self)}")
        logger.setLevel(logging.INFO)
        logger.propagate = False
        logger.handlers.clear()

        handler = logging.FileHandler(log_path)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
        return logger

    def _log_stage(self, loop_idx: int, stage: str, start_time: float, end_time: float) -> None:
        if not self._timing_logger:
            return

        elapsed_sec = time.time() - self._timing_start_time
        self._timing_logger.info(
            "t=%.3fs loop=%d stage=%s start=%.6f end=%.6f dt_ms=%.3f",
            elapsed_sec,
            loop_idx,
            stage,
            start_time,
            end_time,
            (end_time - start_time) * 1000.0,
        )

    def _log_event(self, event: str) -> None:
        if not self._timing_logger:
            return

        elapsed_sec = time.time() - self._timing_start_time
        self._timing_logger.info("event=%s t=%.3fs", event, elapsed_sec)
    
    def run_once(self) -> Telemetry:
        """
        1サイクル分の処理（例外処理や安全停止ポリシーは必要に応じて追加）。
        
        Returns:
            Telemetry: 駆動モジュールの適用結果
        """
        self._loop_index += 1
        loop_idx = self._loop_index

        self._log_event("loop_start")

        # 1. 計測 (Measure)
        t0 = time.perf_counter()
        distance_data = self.sensor.read()
        t1 = time.perf_counter()
        self._log_stage(loop_idx, "sensor_read", t0, t1)
        
        # 2. 知覚 (Perceive)
        t2 = time.perf_counter()
        features = self.perception.analyze(distance_data)
        t3 = time.perf_counter()
        self._log_stage(loop_idx, "perception", t2, t3)
        
        # 3. 判断 (Decide)
        t4 = time.perf_counter()
        command = self.decision.decide(features)
        t5 = time.perf_counter()
        self._log_stage(loop_idx, "decision", t4, t5)
        
        # 4. 実行 (Act)
        t6 = time.perf_counter()
        telemetry = self.actuation.apply(command)
        t7 = time.perf_counter()
        self._log_stage(loop_idx, "actuation", t6, t7)
        self._log_event("loop_end")
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
        start_time = time.time()
        iteration = 0
        last_log_time = 0.0
        header_printed = False
        
        try:
            while max_iterations is None or iteration < max_iterations:
                self._loop_index += 1
                loop_idx = self._loop_index

                self._log_event("loop_start")

                t0 = time.perf_counter()
                distance_data = self.sensor.read()
                t1 = time.perf_counter()
                self._log_stage(loop_idx, "sensor_read", t0, t1)

                t2 = time.perf_counter()
                features = self.perception.analyze(distance_data)
                t3 = time.perf_counter()
                self._log_stage(loop_idx, "perception", t2, t3)

                t4 = time.perf_counter()
                command = self.decision.decide(features)
                t5 = time.perf_counter()
                self._log_stage(loop_idx, "decision", t4, t5)

                t6 = time.perf_counter()
                telemetry = self.actuation.apply(command)
                t7 = time.perf_counter()
                self._log_stage(loop_idx, "actuation", t6, t7)
                self._log_event("loop_end")
                
                # ヘッダーを一度だけ出力
                if not header_printed:
                    print("TIME  | L_DIST | ERROR | STEER | THROTTLE | STATUS")
                    header_printed = True
                
                # 詳細ログ出力（一定間隔で）
                current_time = time.time()
                iteration += 1
                if current_time - last_log_time >= log_interval_sec:
                    elapsed_time = current_time - start_time
                    self._log_cycle(elapsed_time, distance_data, features, command, telemetry)
                    last_log_time = current_time
                
                if loop_interval_sec > 0:
                    time.sleep(loop_interval_sec)
        except KeyboardInterrupt:
            print("\n[Orchestrator] Interrupted by user")
            self.emergency_stop("user_interrupt")
        except Exception as e:
            print(f"\n[Orchestrator] Error occurred: {e}")
            self.emergency_stop(f"error: {str(e)}")
        finally:
            self._log_event("run_stop")
    
    def _log_cycle(
        self,
        elapsed_time: float,
        distance_data: DistanceData,
        features: WallFeatures,
        command: Command,
        telemetry: Telemetry
    ) -> None:
        """
        1サイクルの詳細情報をログ出力（パイプ区切りのテーブル形式）
        
        Args:
            elapsed_time: ループ開始からの経過時間（秒）
            distance_data: センサーデータ
            features: 知覚結果
            command: 判断結果
            telemetry: 駆動結果
        """
        # データ取得
        timestamp = elapsed_time
        l_dist = distance_data.left_mm
        error = features.error_from_target
        steer = command.steer
        speed = command.throttle
        status_str = telemetry.status.value if hasattr(telemetry.status, 'value') else str(telemetry.status)
        
        # パイプ区切りのテーブル形式で出力
        # TIME: 5文字幅（右寄せ）、小数点1桁 + "s"
        # L_DIST: 4文字幅（右寄せ） + "mm"
        # ERROR: 4文字幅（右寄せ）、符号付き + "mm"
        # STEER: 5文字幅（右寄せ）、符号付き、小数点2桁
        # THROTTLE: 6文字幅（右寄せ）、小数点2桁 + 空白調整
        # STATUS: そのまま文字列
        print(f"{timestamp:>5.1f}s | {l_dist:>4.0f}mm | {error:>+4.0f}mm | {steer:>+5.2f} | {speed:>6.2f}   | {status_str}")
    
    def emergency_stop(self, reason: str = "emergency") -> Telemetry:
        """
        上位から明示停止できる入口（設計上の口）。
        
        Args:
            reason: 停止理由
            
        Returns:
            Telemetry: 停止処理の結果
        """
        return self.actuation.stop(reason)
