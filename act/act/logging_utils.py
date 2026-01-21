from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional


def setup_logging(
    log_path: str = "logs/act.log",
    level: int = logging.INFO,
    console: bool = True,
) -> None:
    """アプリ全体のロギング設定を初期化する。"""
    log_file = Path(log_path)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    handlers: list[logging.Handler] = []
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    handlers.append(file_handler)

    if console:
        handlers.append(logging.StreamHandler())

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=handlers,
    )


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """指定名のロガーを取得する。"""
    return logging.getLogger(name)
