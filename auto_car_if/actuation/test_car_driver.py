#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CarDriver ハードウェア動作確認スクリプト

このスクリプトは、実機でCarDriverが正しく動作するか確認するためのものです。
PCA9685、ステアリングサーボ、DCモーターが正しく接続されている必要があります。

実行方法:
    sudo python3 -m auto_car_if.actuation.test_car_driver
    または
    sudo python3 auto_car_if/actuation/test_car_driver.py

注意: I2Cバスへのアクセスには通常sudo権限が必要です。
      または、ユーザーをi2cグループに追加してください。
"""

from __future__ import annotations

import logging
import sys
import time
from typing import Optional

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

try:
    from .motor_driver import CarDriver
except ImportError:
    # 直接実行時用
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from auto_car_if.actuation.motor_driver import CarDriver


def test_steering(driver: CarDriver) -> None:
    """ステアリングの動作テスト
    
    Args:
        driver: CarDriverインスタンス
    """
    logger.info("=" * 50)
    logger.info("ステアリングテスト開始")
    logger.info("=" * 50)
    
    test_sequence = [
        (0.0, "中央位置"),
        (-1.0, "左最大"),
        (1.0, "右最大"),
        (0.0, "中央位置に戻す"),
    ]
    
    for value, description in test_sequence:
        logger.info(f"ステアリング: {description} (value={value:.1f})")
        try:
            driver.set_steering(value)
            time.sleep(1.0)  # 1秒待機して動作を確認
        except Exception as e:
            logger.error(f"ステアリング設定エラー: {e}")
            raise
    
    logger.info("ステアリングテスト完了")


def test_throttle(driver: CarDriver) -> None:
    """スロットルの動作テスト
    
    Args:
        driver: CarDriverインスタンス
    """
    logger.info("=" * 50)
    logger.info("スロットルテスト開始")
    logger.info("=" * 50)
    
    test_sequence = [
        (0.0, "停止"),
        (0.3, "微速前進"),
        (0.0, "停止"),
        (-0.3, "微速後退"),
        (0.0, "停止"),
    ]
    
    for value, description in test_sequence:
        logger.info(f"スロットル: {description} (value={value:.1f})")
        try:
            driver.set_throttle(value)
            if value != 0.0:
                time.sleep(2.0)  # 前進・後退は2秒待機
            else:
                time.sleep(1.0)  # 停止は1秒待機
        except Exception as e:
            logger.error(f"スロットル設定エラー: {e}")
            raise
    
    logger.info("スロットルテスト完了")


def main() -> int:
    """メイン関数
    
    Returns:
        終了コード（0: 成功、1: エラー）
    """
    driver: Optional[CarDriver] = None
    
    try:
        logger.info("CarDriver ハードウェア動作確認スクリプト")
        logger.info("=" * 50)
        logger.info("注意: このスクリプトは実機でモーターとサーボを動作させます")
        logger.info("安全な場所で実行し、緊急停止の準備をしてください")
        logger.info("=" * 50)
        
        # 5秒待機（緊急停止の機会を提供）
        logger.info("5秒後にテストを開始します...")
        for i in range(5, 0, -1):
            logger.info(f"{i}...")
            time.sleep(1.0)
        
        # CarDriverの初期化
        logger.info("CarDriverを初期化中...")
        driver = CarDriver()
        logger.info("CarDriver初期化完了")
        
        # ステアリングテスト
        test_steering(driver)
        
        # 少し待機
        time.sleep(1.0)
        
        # スロットルテスト
        test_throttle(driver)
        
        logger.info("=" * 50)
        logger.info("すべてのテストが正常に完了しました")
        logger.info("=" * 50)
        
        return 0
        
    except KeyboardInterrupt:
        logger.warning("\nユーザーによって中断されました")
        return 130  # SIGINT exit code
        
    except Exception as e:
        logger.error(f"エラーが発生しました: {e}", exc_info=True)
        return 1
        
    finally:
        # 必ずクリーンアップを実行
        if driver is not None:
            logger.info("CarDriverをクリーンアップ中...")
            try:
                driver.cleanup()
                logger.info("クリーンアップ完了")
            except Exception as e:
                logger.error(f"クリーンアップ中にエラー: {e}")


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
