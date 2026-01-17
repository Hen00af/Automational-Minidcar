# --------------------------------
# config/utils.py
# 設定関連のユーティリティ関数
# --------------------------------
from __future__ import annotations

from .hardware import hardware


def set_us(ch, us):
    ch.duty_cycle = int(us / 20000 * 65535)
