from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Protocol, runtime_checkable

class ColorSpace(str, Enum):
    RGB = "RGB"
    BGR = "BGR"

class PixelFormat(str, Enum):
    UINT8 = "uint8"

@runtime_checkable
class ImageBuffer(Protocol):
    """
    Camera module -> Perception の '画像' 最小契約。
    実体は numpy / bytes / custom など何でもよいが、メタ情報と生データ参照ができること。
    """
    @property
    def width(self) -> int: ...
    @property
    def height(self) -> int: ...
    @property
    def channels(self) -> int: ...
    @property
    def pixel_format(self) -> PixelFormat: ...
    @property
    def color_space(self) -> ColorSpace: ...
    def as_bytes(self) -> bytes: ...

@dataclass(frozen=True)
class Frame:
    """
    Camera module -> Perception 入力（1フレーム）。
    - color_space は RGB/BGR のいずれか（前段で正規化する方針）
    """
    frame_id: int
    t_capture_sec: float
    image: ImageBuffer

    # 将来用（第1イテレーションでは未使用でOK）
    camera_id: Optional[str] = None
    exposure_us: Optional[int] = None
    gain: Optional[float] = None

