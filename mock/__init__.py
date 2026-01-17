"""
モック実装パッケージ（開発・テスト用）

Strategyパターンを使用して、異なる状況（Situation）を切り替えてテストできるようにする。
"""
# 新しい構造のコンポーネント
from .sensors import MockSensor
from .actuation import MockActuator
from .situations.base import BaseSituation, DefaultSituation

# ユーティリティ（coreモジュールから）
from .core.utils import get_logger, clamp, linear_interpolate

# 例外（coreモジュールから）
from .core.exceptions import MockError, CalibrationError, SituationError

# Domain models (型定義) - actパッケージから再エクスポート
from act.domain import (
    DistanceData,
    WallFeatures,
    Command,
    DriveMode,
    ActuationCalibration,
    Telemetry,
    ActuationStatus,
)

# Interfaces (プロトコル) - actパッケージから再エクスポート
from act.interfaces import (
    CameraModule,
    DistanceSensorModule,
    Perception,
    Decision,
    Actuation,
)

# Orchestrator - actパッケージから再エクスポート
from act.orchestrator import Orchestrator

__all__ = [
    # 新しい構造のコンポーネント
    "MockSensor",
    "MockActuator",
    "BaseSituation",
    "DefaultSituation",
    # ユーティリティ
    "get_logger",
    "clamp",
    "linear_interpolate",
    # 例外
    "MockError",
    "CalibrationError",
    "SituationError",
    # Domain models
    "DistanceData",
    "WallFeatures",
    "Command",
    "DriveMode",
    "ActuationCalibration",
    "Telemetry",
    "ActuationStatus",
    # Interfaces
    "CameraModule",
    "DistanceSensorModule",
    "Perception",
    "Decision",
    "Actuation",
    # Orchestrator
    "Orchestrator",
]
