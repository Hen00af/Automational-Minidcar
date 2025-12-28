"""Camera module for image acquisition and normalization."""

def __getattr__(name):
    if name == "PiCameraCV":
        from .pi import PiCameraCV
        return PiCameraCV
    if name == "CvImageBuffer":
        from .pi import CvImageBuffer
        return CvImageBuffer
    raise AttributeError(f"module {__name__} has no attribute {name}")

__all__ = ["PiCameraCV", "CvImageBuffer"]
