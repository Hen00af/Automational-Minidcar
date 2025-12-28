"""Pi Camera (OpenCV capture) adapter for Orchestrator.

- Assumes libcamera/Video4Linux device accessible via OpenCV VideoCapture.
- Outputs BGR frames as ImageBuffer for Perception.
"""
from __future__ import annotations

import time
from typing import Iterator, Optional

try:
    import cv2
except ImportError as exc:  # pragma: no cover - runtime dependency
    raise ImportError("OpenCV (cv2) is required for PiCameraCV") from exc

from ..domain.frame import Frame, ColorSpace, PixelFormat, ImageBuffer


class CvImageBuffer(ImageBuffer):
    """Simple ImageBuffer wrapper around an OpenCV ndarray (BGR)."""

    def __init__(self, img):
        self._img = img

    @property
    def width(self) -> int:
        return self._img.shape[1]

    @property
    def height(self) -> int:
        return self._img.shape[0]

    @property
    def channels(self) -> int:
        return 3

    @property
    def pixel_format(self) -> PixelFormat:
        return PixelFormat.UINT8

    @property
    def color_space(self) -> ColorSpace:
        return ColorSpace.BGR

    def as_bytes(self) -> bytes:
        return self._img.tobytes()

    @property
    def ndarray(self):
        """Expose the underlying ndarray for Perception steps that need it."""
        return self._img


class PiCameraCV:
    """OpenCV-based camera provider for Pi Camera Module v2."""

    def __init__(
        self,
        device: int = 0,
        width: int = 320,
        height: int = 240,
        fps: Optional[int] = None,
    ) -> None:
        self.device = device
        self.width = width
        self.height = height
        self.fps = fps
        self.cap = cv2.VideoCapture(device)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        if fps is not None:
            self.cap.set(cv2.CAP_PROP_FPS, fps)
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open camera device {device}")
        self._frame_id = 0

    def frames(self) -> Iterator[Frame]:
        """Generator that yields Frames until capture fails."""
        while True:
            ok, frame = self.cap.read()
            if not ok:
                break
            # frame is BGR ndarray
            yield Frame(
                frame_id=self._frame_id,
                t_capture_sec=time.time(),
                image=CvImageBuffer(frame),
            )
            self._frame_id += 1

    def close(self) -> None:
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def __del__(self):  # pragma: no cover - best-effort cleanup
        try:
            self.close()
        except Exception:
            pass
