"""Perception module for line detection and feature extraction."""

def __getattr__(name):
    if name == "LinePerception":
        from .line import LinePerception
        return LinePerception
    if name == "SensorBasedPerception":
        from .sensor import SensorBasedPerception
        return SensorBasedPerception
    raise AttributeError(f"module {__name__} has no attribute {name}")

__all__ = ["LinePerception", "SensorBasedPerception"]
