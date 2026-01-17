"""
状況（Situation）モジュール

Strategyパターンを使用して、異なる状況を切り替えてテストできるようにする。
"""
from .base import BaseSituation, DefaultSituation

__all__ = ["BaseSituation", "DefaultSituation"]
