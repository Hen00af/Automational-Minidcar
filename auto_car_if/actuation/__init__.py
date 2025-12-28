"""Actuation module for hardware control."""


import platform

def __getattr__(name):
    if name == "PWMActuation":
        # Use mock on non-Linux (e.g., macOS, Windows), real on Linux (Raspberry Pi)
        if platform.system() != "Linux":
            from .mock import PWMActuation
        else:
            from .pwm import PWMActuation
        return PWMActuation
    raise AttributeError(f"module {__name__} has no attribute {name}")

__all__ = ["PWMActuation"]
