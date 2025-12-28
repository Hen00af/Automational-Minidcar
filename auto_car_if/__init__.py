# auto_car_if package
from .domain import (
    Frame, ImageBuffer, ColorSpace, PixelFormat,
    Features, PerceptionStatus,
    Command, DriveMode,
    VehicleState,
    ActuationCalibration, Telemetry, ActuationStatus,
)
from .interfaces.protocols import CameraModule, Perception, Decision, Actuation
from .main import Orchestrator

# Lazy-load hardware modules (optional dependencies)
def __getattr__(name):
    if name == "PiCameraCV":
        from .camera import PiCameraCV
        return PiCameraCV
    if name == "CvImageBuffer":
        from .camera import CvImageBuffer
        return CvImageBuffer
    if name == "LinePerception":
        from .perception import LinePerception
        return LinePerception
    if name == "SimpleDecision":
        from .decision import SimpleDecision
        return SimpleDecision
    if name == "PWMActuation":
        from .actuation import PWMActuation
        return PWMActuation
    raise AttributeError(f"module {__name__} has no attribute {name}")

__all__ = [
    "Frame",
    "ImageBuffer",
    "ColorSpace",
    "PixelFormat",
    "Features",
    "PerceptionStatus",
    "Command",
    "DriveMode",
    "VehicleState",
    "ActuationCalibration",
    "Telemetry",
    "ActuationStatus",
    "CameraModule",
    "Perception",
    "Decision",
    "Actuation",
    "Orchestrator",
    "PiCameraCV",
    "CvImageBuffer",
    "LinePerception",
    "SimpleDecision",
    "PWMActuation",
]

