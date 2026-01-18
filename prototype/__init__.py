# act package
# TOFセンサーを用いたミニカー自律走行システムのインターフェース・制御中核

# Domain models (型定義)
from .domain import (
    DistanceData,
    WallFeatures,
    Command,
    DriveMode,
    ActuationCalibration,
    Telemetry,
    ActuationStatus,
)

# Interfaces (プロトコル)
from .interfaces import (
    CameraModule,
    DistanceSensorModule,
    Perception,
    Decision,
    Actuation,
)

# Orchestrator
from .orchestrator import Orchestrator

# Legacy types (後方互換性のため残す)
try:
    from .types_frame import Frame, ImageBuffer, ColorSpace, PixelFormat
    from .types_features import Features, PerceptionStatus
    from .types_vehicle_state import VehicleState
except ImportError:
    # これらの型が削除されている場合は無視
    pass

__all__ = [
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
