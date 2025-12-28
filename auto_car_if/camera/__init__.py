"""Camera module for image acquisition and normalization."""


import sys
import platform

def __getattr__(name):
    if name == "PiCameraCV":
        # Use mock on non-Linux (e.g., macOS, Windows), real on Linux (Raspberry Pi)
        if platform.system() != "Linux":
            from .mock import PiCameraCV
        else:
            from .pi import PiCameraCV
        return PiCameraCV
    if name == "CvImageBuffer":
        from .pi import CvImageBuffer
        return CvImageBuffer
    raise AttributeError(f"module {__name__} has no attribute {name}")

__all__ = ["PiCameraCV", "CvImageBuffer"]
