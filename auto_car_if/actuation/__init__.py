"""Actuation module for hardware control."""

def __getattr__(name):
    if name == "PWMActuation":
        from .pwm import PWMActuation
        return PWMActuation
    raise AttributeError(f"module {__name__} has no attribute {name}")

__all__ = ["PWMActuation"]
