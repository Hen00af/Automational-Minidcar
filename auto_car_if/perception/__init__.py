"""Perception module for line detection and feature extraction."""

def __getattr__(name):
    if name == "LinePerception":
        from .line import LinePerception
        return LinePerception
    raise AttributeError(f"module {__name__} has no attribute {name}")

__all__ = ["LinePerception"]
