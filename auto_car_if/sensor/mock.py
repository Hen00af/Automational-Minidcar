"""Mock sensor implementations for local development (no hardware required)."""
from __future__ import annotations

import time
from typing import Iterator

from ..domain.sensor import SensorReading, SensorType
from ..interfaces.protocols import SensorModule


class UltrasonicSensor(SensorModule):
    """
    Mock ultrasonic sensor for development/testing.
    
    Generates dummy distance readings that simulate a sensor detecting
    obstacles at various distances.
    """
    def __init__(
        self,
        gpio_trigger: int = 23,
        gpio_echo: int = 24,
        min_distance_cm: float = 2.0,
        max_distance_cm: float = 400.0,
    ):
        self.gpio_trigger = gpio_trigger
        self.gpio_echo = gpio_echo
        self.min_distance_cm = min_distance_cm
        self.max_distance_cm = max_distance_cm
        self._reading_id = 0
        self._simulated_distance = 50.0  # Simulated distance in cm

    def readings(self) -> Iterator[SensorReading]:
        """Generate mock sensor readings."""
        while True:
            t_capture = time.time()
            # Simulate distance measurement (can be modified for testing)
            distance = self._simulated_distance
            
            reading = SensorReading(
                reading_id=self._reading_id,
                t_capture_sec=t_capture,
                distance_cm=distance if self.min_distance_cm <= distance <= self.max_distance_cm else None,
                sensor_type=SensorType.ULTRASONIC,
                sensor_id="front",
                quality=1.0 if distance is not None else 0.0,
                raw_value=distance,
            )
            
            self._reading_id += 1
            yield reading
            
            # Simulate sensor reading interval
            time.sleep(0.1)  # 10Hz sampling rate

    def set_simulated_distance(self, distance_cm: float) -> None:
        """Set simulated distance for testing (mock only)."""
        self._simulated_distance = distance_cm

