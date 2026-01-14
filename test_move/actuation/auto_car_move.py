"""Movement Abstraction Layer for autonomous mini car.

This module provides a high-level interface for car movement operations,
wrapping the low-level CarDriver class with intuitive methods.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from auto_car_if.actuation.motor_driver import CarDriver

logger = logging.getLogger(__name__)


class AutoCarMove:
    """High-level movement abstraction layer for autonomous car control.
    
    This class wraps CarDriver and provides intuitive movement commands
    like make_straight(), make_left(), make_right(), and stop().
    
    Design Principles:
    - Dependency Injection: CarDriver is injected via constructor
    - Type Safety: All methods have type hints
    - Readability: Method names are self-documenting
    """
    
    def __init__(self, driver: CarDriver) -> None:
        """Initialize AutoCarMove with a CarDriver instance.
        
        Args:
            driver: Initialized CarDriver instance for hardware control.
            
        Raises:
            TypeError: If driver is not a CarDriver instance.
        """
        if driver is None:
            raise ValueError("driver cannot be None")
        self._driver = driver
        logger.info("AutoCarMove initialized")
    
    def make_straight(self, speed: float) -> None:
        """Move straight ahead at specified speed.
        
        Sets steering to center (0.0) and applies forward throttle.
        
        Args:
            speed: Forward speed in range [0.0, 1.0]
                - 0.0: Stop
                - 1.0: Maximum forward speed
                
        Raises:
            RuntimeError: If driver operation fails.
        """
        if not (0.0 <= speed <= 1.0):
            logger.warning(f"Speed {speed} out of range [0.0, 1.0], clamping")
            speed = max(0.0, min(1.0, speed))
        
        try:
            # Set steering to center
            self._driver.set_steering(0.0)
            # Apply forward throttle
            self._driver.set_throttle(speed)
            logger.debug(f"Moving straight at speed {speed:.3f}")
        except Exception as exc:
            logger.error(f"Failed to move straight: {exc}")
            raise RuntimeError(f"Straight movement failed: {exc}") from exc
    
    def make_right(self, intensity: float, speed: float) -> None:
        """Turn right while moving forward.
        
        Args:
            intensity: Turn intensity in range [0.0, 1.0]
                - 0.0: No turn (straight)
                - 1.0: Maximum right turn
            speed: Forward speed in range [0.0, 1.0]
                - 0.0: Stop
                - 1.0: Maximum forward speed
                
        Raises:
            RuntimeError: If driver operation fails.
        """
        if not (0.0 <= intensity <= 1.0):
            logger.warning(f"Intensity {intensity} out of range [0.0, 1.0], clamping")
            intensity = max(0.0, min(1.0, intensity))
        
        if not (0.0 <= speed <= 1.0):
            logger.warning(f"Speed {speed} out of range [0.0, 1.0], clamping")
            speed = max(0.0, min(1.0, speed))
        
        try:
            # Set steering to right (positive value)
            # CarDriver.set_steering: +1.0 = maximum right
            self._driver.set_steering(intensity)
            # Apply forward throttle
            self._driver.set_throttle(speed)
            logger.debug(f"Turning right: intensity={intensity:.3f}, speed={speed:.3f}")
        except Exception as exc:
            logger.error(f"Failed to turn right: {exc}")
            raise RuntimeError(f"Right turn failed: {exc}") from exc
    
    def make_left(self, intensity: float, speed: float) -> None:
        """Turn left while moving forward.
        
        Args:
            intensity: Turn intensity in range [0.0, 1.0]
                - 0.0: No turn (straight)
                - 1.0: Maximum left turn
            speed: Forward speed in range [0.0, 1.0]
                - 0.0: Stop
                - 1.0: Maximum forward speed
                
        Raises:
            RuntimeError: If driver operation fails.
        """
        if not (0.0 <= intensity <= 1.0):
            logger.warning(f"Intensity {intensity} out of range [0.0, 1.0], clamping")
            intensity = max(0.0, min(1.0, intensity))
        
        if not (0.0 <= speed <= 1.0):
            logger.warning(f"Speed {speed} out of range [0.0, 1.0], clamping")
            speed = max(0.0, min(1.0, speed))
        
        try:
            # Set steering to left (negative value)
            # CarDriver.set_steering: -1.0 = maximum left
            self._driver.set_steering(-intensity)
            # Apply forward throttle
            self._driver.set_throttle(speed)
            logger.debug(f"Turning left: intensity={intensity:.3f}, speed={speed:.3f}")
        except Exception as exc:
            logger.error(f"Failed to turn left: {exc}")
            raise RuntimeError(f"Left turn failed: {exc}") from exc
    
    def stop(self) -> None:
        """Stop the vehicle immediately.
        
        Stops both steering (returns to center) and motor.
        
        Raises:
            RuntimeError: If driver operation fails.
        """
        try:
            self._driver.stop()
            logger.info("Vehicle stopped")
        except Exception as exc:
            logger.error(f"Failed to stop: {exc}")
            raise RuntimeError(f"Stop failed: {exc}") from exc
