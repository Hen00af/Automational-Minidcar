# auto_car_if package
from .types_frame import Frame, ImageBuffer, ColorSpace, PixelFormat
from .types_features import Features, PerceptionStatus
from .types_command import Command, DriveMode
from .types_vehicle_state import VehicleState
from .types_actuation import ActuationCalibration, Telemetry, ActuationStatus
from .protocols import CameraModule, Perception, Decision, Actuation
from .orchestrator_skeleton import Orchestrator

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

