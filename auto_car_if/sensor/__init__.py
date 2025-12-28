"""Sensor module for distance measurement (ultrasonic, infrared, etc.)."""

import platform

def __getattr__(name):
    if name == "UltrasonicSensor":
        # Use mock on non-Linux (e.g., macOS, Windows), real on Linux (Raspberry Pi)
        if platform.system() != "Linux":
            from .mock import UltrasonicSensor
        else:
            # TODO: Implement real ultrasonic sensor driver
            from .mock import UltrasonicSensor
        return UltrasonicSensor
    raise AttributeError(f"module {__name__} has no attribute {name}")

__all__ = ["UltrasonicSensor"]

