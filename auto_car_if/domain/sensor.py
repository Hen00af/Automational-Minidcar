"""Sensor domain models for distance sensors (ultrasonic, infrared, etc.)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class SensorType(str, Enum):
    """Sensor type enumeration."""
    ULTRASONIC = "ultrasonic"
    INFRARED = "infrared"
    LIDAR = "lidar"


@dataclass(frozen=True)
class SensorReading:
    """
    Sensor module -> Perception 入力（1測定値）。
    
    Attributes:
        reading_id: Unique identifier for this reading
        t_capture_sec: Timestamp when the reading was taken
        distance_mm: Distance measurement in millimeters (None if invalid)
        sensor_type: Type of sensor (ultrasonic, infrared, etc.)
        sensor_id: Optional identifier for multiple sensors
        quality: Measurement quality/confidence [0.0, 1.0]
        raw_value: Optional raw sensor value for debugging
    """
    reading_id: int
    t_capture_sec: float
    distance_mm: Optional[float]  # None if out of range or invalid
    sensor_type: SensorType
    sensor_id: Optional[str] = None
    quality: float = 1.0  # [0.0, 1.0]
    raw_value: Optional[float] = None  # For debugging

