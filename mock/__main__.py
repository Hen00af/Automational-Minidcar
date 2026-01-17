#!/usr/bin/env python3
"""
モック実装のエントリーポイント

使用方法:
    python -m mock

または:
    python -m mock --verbose
"""
import sys
import logging
from typing import Optional

from act.orchestrator import Orchestrator
from act.perception import WallPositionPerception
from act.decision import WallFollowDecision
from act.domain.actuation import ActuationCalibration

from mock.sensors import MockSensor
from mock.actuation import MockActuator
from mock.situations.base import DefaultSituation
from mock.config.constants import (
    DEFAULT_LEFT_DISTANCE_MM,
    DEFAULT_FRONT_DISTANCE_MM,
    DEFAULT_RIGHT_DISTANCE_MM,
    DEFAULT_TARGET_DISTANCE_MM,
    DEFAULT_BASE_SPEED,
    DEFAULT_STEER_CENTER_US,
    DEFAULT_STEER_LEFT_US,
    DEFAULT_STEER_RIGHT_US,
    DEFAULT_THROTTLE_STOP_US,
    DEFAULT_THROTTLE_MAX_US,
    DEFAULT_LOOP_INTERVAL_SEC,
    DEFAULT_LOG_INTERVAL_SEC,
)
from mock.core.utils import get_logger


def create_default_calibration() -> ActuationCalibration:
    """
    デフォルトのキャリブレーション設定を作成
    
    Returns:
        キャリブレーション設定
    """
    return ActuationCalibration(
        steer_center_us=DEFAULT_STEER_CENTER_US,
        steer_left_us=DEFAULT_STEER_LEFT_US,
        steer_right_us=DEFAULT_STEER_RIGHT_US,
        throttle_stop_us=DEFAULT_THROTTLE_STOP_US,
        throttle_max_us=DEFAULT_THROTTLE_MAX_US
    )


def setup_logging(verbose: bool = False) -> None:
    """
    ロギングの設定
    
    Args:
        verbose: Trueの場合、DEBUGレベルまで出力する
    """
    level = logging.DEBUG if verbose else logging.INFO
    logger = get_logger("mock")
    logger.setLevel(level)
    
    # 既存のハンドラーをクリア
    logger.handlers.clear()
    
    # 新しいハンドラーを追加
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '[%(levelname)s] %(name)s: %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)


def main(
    verbose: bool = False,
    loop_interval_sec: float = DEFAULT_LOOP_INTERVAL_SEC,
    log_interval_sec: float = DEFAULT_LOG_INTERVAL_SEC,
    situation: Optional[DefaultSituation] = None
) -> int:
    """
    メイン関数
    
    Args:
        verbose: Trueの場合、詳細ログを出力する
        loop_interval_sec: ループ間隔（秒）
        log_interval_sec: ログ出力間隔（秒）
        situation: 使用するSituation（Noneの場合はDefaultSituationを使用）
    
    Returns:
        終了コード（0: 正常終了、1: エラー）
    """
    setup_logging(verbose)
    logger = get_logger("mock")
    
    try:
        logger.info("Initializing components...")
        
        # Situationを作成（デフォルトの状況：壁沿い走行）
        if situation is None:
            situation = DefaultSituation(
                left_distance=DEFAULT_LEFT_DISTANCE_MM,
                front_distance=DEFAULT_FRONT_DISTANCE_MM,
                right_distance=DEFAULT_RIGHT_DISTANCE_MM
            )
        
        # MockSensorにSituationを注入（Dependency Injection）
        sensor = MockSensor(situation=situation, verbose=verbose)
        
        # その他のコンポーネントを初期化
        perception = WallPositionPerception(target_distance_mm=DEFAULT_TARGET_DISTANCE_MM)
        decision = WallFollowDecision(base_speed=DEFAULT_BASE_SPEED)
        actuation = MockActuator(verbose=verbose)
        
        # キャリブレーションを設定
        calib = create_default_calibration()
        actuation.configure(calib)
        
        # オーケストレーターを作成
        orchestrator = Orchestrator(sensor, perception, decision, actuation)
        
        logger.info("Starting loop (Ctrl+C to stop)...")
        logger.info("Loop interval: %.1fs (%.1fHz), Log interval: %.1fs",
                   loop_interval_sec, 1.0 / loop_interval_sec, log_interval_sec)
        logger.info("Situation: %s", type(situation).__name__)
        
        orchestrator.run_loop(
            loop_interval_sec=loop_interval_sec,
            log_interval_sec=log_interval_sec
        )
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Stopped by user")
        return 0
    except Exception as e:
        logger.error("Error occurred: %s", e, exc_info=True)
        return 1
    finally:
        try:
            actuation.close()
            sensor.close()
        except NameError:
            # 初期化前にエラーが発生した場合
            pass


if __name__ == "__main__":
    # コマンドライン引数の解析（簡易版）
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    sys.exit(main(verbose=verbose))
