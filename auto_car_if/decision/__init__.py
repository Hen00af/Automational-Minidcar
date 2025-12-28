"""Decision module for control logic."""

def __getattr__(name):
    if name == "SimpleDecision":
        from .simple import SimpleDecision
        return SimpleDecision
    raise AttributeError(f"module {__name__} has no attribute {name}")

__all__ = ["SimpleDecision"]
