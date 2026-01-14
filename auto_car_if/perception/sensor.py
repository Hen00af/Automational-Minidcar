"""Sensor-based perception module (for future use when replacing camera with sensors)."""
from __future__ import annotations

from ..domain.sensor import SensorReading
from ..domain.features import Features, PerceptionStatus
from ..interfaces.protocols import SensorPerception


class SensorBasedPerception(SensorPerception):
    """
    Perception module that processes sensor readings instead of camera frames.
    
    This is designed for future use when replacing camera-based navigation
    with ultrasonic or infrared sensor-based navigation.
    
    Converts distance measurements into lateral_bias and quality metrics.
    """
    def __init__(
        self,
        safe_distance_mm: float = 200.0,
        critical_distance_mm: float = 100.0,
        left_sensor_id: str = "left",
        right_sensor_id: str = "right",
        front_sensor_id: str = "front",
    ):
        self.safe_distance_mm = safe_distance_mm
        self.critical_distance_mm = critical_distance_mm
        self.left_sensor_id = left_sensor_id
        self.right_sensor_id = right_sensor_id
        self.front_sensor_id = front_sensor_id
        
        # Store recent readings from multiple sensors
        self._recent_readings: dict[str, SensorReading] = {}

    def process_sensor(self, reading: SensorReading) -> Features:
        """
        Process a single sensor reading and convert it to Features.
        
        For multi-sensor setups, this should be called for each sensor,
        and the results should be combined.
        """
        # Store reading for multi-sensor fusion
        if reading.sensor_id:
            self._recent_readings[reading.sensor_id] = reading
        
        # Calculate lateral_bias based on left/right sensor difference
        # If only front sensor, use distance to determine behavior
        lateral_bias = 0.0
        quality = reading.quality if reading.distance_mm is not None else 0.0
        
        if reading.sensor_id == self.front_sensor_id:
            # Front sensor: use distance to determine if we should slow/stop
            if reading.distance_mm is None:
                status = PerceptionStatus.INSUFFICIENT_SIGNAL
            elif reading.distance_mm < self.critical_distance_mm:
                status = PerceptionStatus.INSUFFICIENT_SIGNAL  # Too close, stop
            elif reading.distance_mm < self.safe_distance_mm:
                status = PerceptionStatus.OK  # Close but manageable
            else:
                status = PerceptionStatus.OK  # Safe distance
        else:
            # Left/Right sensor: calculate lateral bias
            left_dist = self._recent_readings.get(self.left_sensor_id, reading).distance_mm
            right_dist = self._recent_readings.get(self.right_sensor_id, reading).distance_mm
            
            if left_dist is not None and right_dist is not None:
                # Bias towards the side with more distance
                diff = right_dist - left_dist
                max_diff = 500.0  # Normalize to [-1, 1] (500mm = 50cm)
                lateral_bias = max(-1.0, min(1.0, diff / max_diff))
                status = PerceptionStatus.OK
            else:
                status = PerceptionStatus.INSUFFICIENT_SIGNAL
        
        # Store distance in signals for Decision module
        signals = {
            "distance_mm": reading.distance_mm if reading.distance_mm else 0.0,
            "sensor_type": reading.sensor_type.value,
        }
        
        return Features(
            frame_id=reading.reading_id,
            t_capture_sec=reading.t_capture_sec,
            lateral_bias=lateral_bias,
            quality=quality,
            status=status,
            signals=signals,
            debug={
                "sensor_id": reading.sensor_id,
                "raw_value": reading.raw_value,
            },
        )

