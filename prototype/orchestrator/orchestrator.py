# --------------------------------
# センサー→知覚→判断→駆動のループを統合実行するオーケストレーター
# --------------------------------
from __future__ import annotations

import logging
import os
from typing import Optional

from ..interfaces.protocols import DistanceSensorModule, Perception, Decision, Actuation
from ..domain.actuation import Telemetry
from ..domain.distance import DistanceData
from ..domain.features import WallFeatures
from ..domain.command import Command
from ..config import orchestrator


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
        timing_log_path: Optional[str] = None,
    ):
        """
        初期化

        Args:
            sensor: 距離センサーモジュール
            perception: 知覚モジュール
            decision: 判断モジュール
            actuation: 駆動モジュール
            timing_log_path: タイミングログファイルのパス（Noneの場合はログを出力しない）
        """
        self.sensor = sensor
        self.perception = perception
        self.decision = decision
        self.actuation = actuation
        self._last_sensor_time: Optional[float] = None
        self._last_actuation_time: Optional[float] = None
        self._last_loop_time: Optional[float] = None
        self._timing_logger = self._setup_timing_logger(timing_log_path)
        import time

        self._timing_start_time = time.time()
        if self._timing_logger:
            self._timing_logger.info("event=run_start t=%.3fs", 0.0)

    def run_once(self) -> Telemetry:
        """
        1サイクル分の処理（例外処理や安全停止ポリシーは必要に応じて追加）。

        Returns:
            Telemetry: 駆動モジュールの適用結果
        """
        import time

        loop_idx = 0
        t0 = time.perf_counter()

        # 1. 計測 (Measure)
        t1 = time.perf_counter()
        distance_data = self.sensor.read()
        t2 = time.perf_counter()
        self._log_stage(loop_idx, "sensor", t1, t2)

        # 2. 知覚 (Perceive)
        t3 = time.perf_counter()
        features = self.perception.analyze(distance_data)
        t4 = time.perf_counter()
        self._log_stage(loop_idx, "perception", t3, t4)

        # 3. 判断 (Decide)
        t5 = time.perf_counter()
        command = self.decision.decide(features)
        t6 = time.perf_counter()
        self._log_stage(loop_idx, "decision", t5, t6)

        # 4. 実行 (Act)
        t7 = time.perf_counter()
        telemetry = self.actuation.apply(command)
        t8 = time.perf_counter()
        self._log_stage(loop_idx, "actuation", t7, t8)

        self._log_event("loop_end")
        self._log_frequency(loop_idx, t1, t7, t0)
        return telemetry

    def run_loop(
        self,
        max_iterations: Optional[int] = None,
        poll_interval_sec: float = orchestrator.POLL_INTERVAL_SEC,
        log_interval_sec: float = orchestrator.LOG_INTERVAL_SEC,
    ) -> None:
        """
        ポーリングベースの連続実行。
        sensor.poll() で data-ready なセンサーのみ読み出し、
        更新があったときだけ perception→decision→actuation を実行する。

        Args:
            max_iterations: 最大実行回数（Noneの場合は無限ループ）
            poll_interval_sec: ポーリング間隔（秒）。デフォルトは設定ファイルの値（1ms）
            log_interval_sec: 詳細ログ出力間隔（秒）。デフォルトは設定ファイルの値
        """
        import time

        start_time = time.time()
        iteration = 0
        last_log_time = 0.0
        header_printed = False

        try:
            while max_iterations is None or iteration < max_iterations:
                t0 = time.perf_counter()

                # 1. ポーリング (Poll)
                t1 = time.perf_counter()
                updated, distance_data = self.sensor.poll()
                t2 = time.perf_counter()
                self._log_stage(iteration, "sensor", t1, t2)

                # 更新なしならスキップして次のポーリングへ
                if not updated:
                    time.sleep(poll_interval_sec)
                    continue

                # 2. 知覚 (Perceive)
                t3 = time.perf_counter()
                features = self.perception.analyze(distance_data)
                t4 = time.perf_counter()
                self._log_stage(iteration, "perception", t3, t4)

                # 3. 判断 (Decide)
                t5 = time.perf_counter()
                command = self.decision.decide(features)
                t6 = time.perf_counter()
                self._log_stage(iteration, "decision", t5, t6)

                # 4. 実行 (Act)
                t7 = time.perf_counter()
                telemetry = self.actuation.apply(command)
                t8 = time.perf_counter()
                self._log_stage(iteration, "actuation", t7, t8)

                # ヘッダーを一度だけ出力
                if not header_printed:
                    print(
                        "TIME   | F_DIST | L_DIST | LF_DIST | ERROR   | FRONT | L_WALL | STEER | THROTTLE | STEER_PWM | THROTTLE_PWM | STATUS"
                    )
                    header_printed = True

                # 詳細ログ出力（一定間隔で）
                current_time = time.time()
                iteration += 1
                if current_time - last_log_time >= log_interval_sec:
                    elapsed_time = current_time - start_time
                    self._log_cycle(
                        elapsed_time, distance_data, features, command, telemetry
                    )
                    last_log_time = current_time

                self._log_event("loop_end")
                self._log_frequency(iteration, t1, t7, t0)

                time.sleep(poll_interval_sec)
        except KeyboardInterrupt:
            print("\n[Orchestrator] Interrupted by user")
            self.emergency_stop("user_interrupt")
        except Exception as e:
            print(f"\n[Orchestrator] Error occurred: {e}")
            self.emergency_stop(f"error: {str(e)}")

    def _setup_timing_logger(
        self, timing_log_path: Optional[str]
    ) -> Optional[logging.Logger]:
        """
        タイミングロガーをセットアップ

        Args:
            timing_log_path: ログファイルのパス（Noneの場合はログを出力しない）

        Returns:
            設定されたロガー。timing_log_pathがNoneの場合はNone
        """
        if timing_log_path is None:
            return None

        # ログディレクトリが存在しない場合は作成
        log_dir = os.path.dirname(timing_log_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # ロガーを作成
        logger = logging.getLogger(f"{__name__}.timing")
        logger.setLevel(logging.INFO)

        # 既存のハンドラーをクリア（重複を防ぐ）
        logger.handlers.clear()

        # ファイルハンドラーを作成
        file_handler = logging.FileHandler(timing_log_path, mode="w", encoding="utf-8")
        file_handler.setLevel(logging.INFO)

        # フォーマッターを設定（シンプルな形式）
        formatter = logging.Formatter("%(message)s")
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.propagate = False  # 親ロガーに伝播しない

        return logger

    def _log_event(self, event: str) -> None:
        """
        イベントをログに記録

        Args:
            event: イベント名（例: "run_start", "loop_end"）
        """
        if not self._timing_logger:
            return

        import time

        elapsed_sec = time.time() - self._timing_start_time
        self._timing_logger.info("event=%s t=%.3fs", event, elapsed_sec)

    def _log_stage(
        self, loop_idx: int, stage_name: str, start_time: float, end_time: float
    ) -> None:
        """
        各ステージの処理時間をログに記録

        Args:
            loop_idx: ループインデックス
            stage_name: ステージ名（"sensor", "perception", "decision", "actuation"）
            start_time: 開始時刻
            end_time: 終了時刻
        """
        if not self._timing_logger:
            return

        duration = end_time - start_time
        import time

        elapsed_sec = time.time() - self._timing_start_time
        self._timing_logger.info(
            "t=%.3fs loop=%d stage=%s duration=%.6fs",
            elapsed_sec,
            loop_idx,
            stage_name,
            duration,
        )

    def _log_frequency(
        self, loop_idx: int, sensor_time: float, actuation_time: float, loop_time: float
    ) -> None:
        """
        センサー/駆動/ループの実測周波数（Hz）をログに記録

        Args:
            loop_idx: ループインデックス
            sensor_time: センサー読み取り時刻
            actuation_time: 駆動実行時刻
            loop_time: ループ開始時刻
        """
        if not self._timing_logger:
            return

        sensor_hz = self._calculate_hz(sensor_time, self._last_sensor_time)
        actuation_hz = self._calculate_hz(actuation_time, self._last_actuation_time)
        loop_hz = self._calculate_hz(loop_time, self._last_loop_time)

        import time

        elapsed_sec = time.time() - self._timing_start_time
        self._timing_logger.info(
            "t=%.3fs loop=%d metric=frequency sensor_hz=%s actuation_hz=%s loop_hz=%s",
            elapsed_sec,
            loop_idx,
            self._format_hz(sensor_hz),
            self._format_hz(actuation_hz),
            self._format_hz(loop_hz),
        )

        self._last_sensor_time = sensor_time
        self._last_actuation_time = actuation_time
        self._last_loop_time = loop_time

    @staticmethod
    def _calculate_hz(
        current_time: float, last_time: Optional[float]
    ) -> Optional[float]:
        """
        前回時刻と現在時刻から周波数（Hz）を計算

        Args:
            current_time: 現在時刻
            last_time: 前回時刻

        Returns:
            周波数（Hz）。初回や時刻が無効な場合はNone
        """
        if last_time is None:
            return None
        dt = current_time - last_time
        if dt <= 0:
            return None
        return 1.0 / dt

    @staticmethod
    def _format_hz(value: Optional[float]) -> str:
        """
        周波数値を文字列にフォーマット

        Args:
            value: 周波数値（Hz）

        Returns:
            フォーマットされた文字列。Noneの場合は"NA"
        """
        if value is None:
            return "NA"
        return f"{value:.2f}"

    def _log_cycle(
        self,
        elapsed_time: float,
        distance_data: DistanceData,
        features: WallFeatures,
        command: Command,
        telemetry: Telemetry,
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
        f_dist = distance_data.front_mm
        l_dist = distance_data.left_mm
        lf_dist = distance_data.left_front_mm
        error = features.error_from_target
        steer = command.steer
        speed = command.throttle
        steer_pwm = telemetry.steer_pwm_us if telemetry.steer_pwm_us is not None else 0
        throttle_pwm = (
            telemetry.throttle_pwm_us if telemetry.throttle_pwm_us is not None else 0
        )
        status_str = (
            telemetry.status.value
            if hasattr(telemetry.status, "value")
            else str(telemetry.status)
        )

        # 知覚結果のフラグ
        front_flag = "Y" if features.is_front_blocked else "N"
        left_wall_flag = "Y" if features.is_left_wall else "N"

        # パイプ区切りのテーブル形式で出力
        print(
            f"{timestamp:>5.1f}s | {f_dist:>4.0f}mm | {l_dist:>4.0f}mm | {lf_dist:>5.0f}mm | {error:>+5.0f}mm | {front_flag:>5} | {left_wall_flag:>6} | {steer:>+5.2f} | {speed:>6.2f}   | {steer_pwm:>7}us | {throttle_pwm:>9}us |  {status_str}"
        )

    def emergency_stop(self, reason: str = "emergency") -> Telemetry:
        """
        上位から明示停止できる入口（設計上の口）。

        Args:
            reason: 停止理由

        Returns:
            Telemetry: 停止処理の結果
        """
        return self.actuation.stop(reason)
