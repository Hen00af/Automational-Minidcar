"""Simple line perception for centerline tracking (BGR input).

- Uses bottom ROI and threshold (OTSU) to find line mask.
- Outputs lateral_bias in [-1, +1] and quality in [0,1].
"""
from __future__ import annotations

from typing import Dict, Optional

try:
    import cv2
    import numpy as np
except ImportError as exc:  # pragma: no cover - runtime dependency
    raise ImportError("OpenCV (cv2) and numpy are required for LinePerception") from exc

from ..domain.frame import Frame
from ..domain.features import Features, PerceptionStatus


class LinePerception:
    def __init__(
        self,
        roi_ratio: float = 0.35,
        quality_thresh: float = 0.2,
        blur_kernel: int = 3,
    ) -> None:
        self.roi_ratio = roi_ratio
        self.quality_thresh = quality_thresh
        self.blur_kernel = blur_kernel

    def process(self, frame: Frame) -> Features:
        img = getattr(frame.image, "ndarray", None)
        if img is None:
            return Features(
                frame_id=frame.frame_id,
                t_capture_sec=frame.t_capture_sec,
                lateral_bias=0.0,
                quality=0.0,
                status=PerceptionStatus.INVALID_INPUT,
                debug={"message": "image buffer missing ndarray"},
            )

        h, w = img.shape[:2]
        roi = img[int(h * (1 - self.roi_ratio)) :, :]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        if self.blur_kernel > 1:
            gray = cv2.GaussianBlur(gray, (self.blur_kernel, self.blur_kernel), 0)

        _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        M = cv2.moments(mask)
        if M["m00"] == 0:
            return Features(
                frame_id=frame.frame_id,
                t_capture_sec=frame.t_capture_sec,
                lateral_bias=0.0,
                quality=0.0,
                status=PerceptionStatus.INSUFFICIENT_SIGNAL,
                debug={"message": "no line detected"},
            )

        cx = int(M["m10"] / M["m00"])
        lateral_bias = (cx - w / 2) / (w / 2)
        quality = float(min(1.0, M["m00"] / (w * roi.shape[0] * 255)))
        status = PerceptionStatus.OK if quality >= self.quality_thresh else PerceptionStatus.INSUFFICIENT_SIGNAL

        debug: Dict[str, float] = {
            "cx": float(cx),
            "width": float(w),
            "roi_height": float(roi.shape[0]),
        }

        return Features(
            frame_id=frame.frame_id,
            t_capture_sec=frame.t_capture_sec,
            lateral_bias=float(lateral_bias),
            quality=quality,
            status=status,
            debug=debug,
        )
