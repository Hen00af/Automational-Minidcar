"""PCA9685-based motor driver for steering servo and DC motor control.

This module provides CarDriver class that wraps PCA9685 I2C PWM driver
for controlling a steering servo and a DC motor via H-bridge driver.
"""
from __future__ import annotations

import logging
from typing import Optional

try:
    import board
    import busio
    from adafruit_motor.motor import DCMotor
    from adafruit_pca9685 import PCA9685
except ImportError as exc:
    raise ImportError(
        "PCA9685 libraries required: adafruit-circuitpython-pca9685, "
        "adafruit-circuitpython-motor, adafruit-blinka"
    ) from exc

logger = logging.getLogger(__name__)


class CarDriver:
    """PCA9685-based driver for car steering and throttle control.

    This class manages:
    - Steering servo on PCA9685 Channel 0
    - DC motor via H-bridge on PCA9685 Channels 1 & 2

    Hardware Configuration:
    - I2C Bus: SDA=GPIO2, SCL=GPIO3
    - PCA9685 Address: 0x40
    - PCA9685 Frequency: 50Hz
    - Steering Servo: Channel 0
    - DC Motor: Channels 1 & 2 (H-bridge control)
    """

    # Default servo pulse widths (in microseconds)
    # These values should be calibrated for your specific servo
    STEER_CENTER_US = 1500  # Center position
    STEER_LEFT_US = 1000    # Maximum left (steer=+1.0)
    STEER_RIGHT_US = 2000   # Maximum right (steer=-1.0)

    def __init__(
        self,
        i2c_address: int = 0x40,
        frequency: int = 50,
        steer_channel: int = 0,
        motor_channel1: int = 1,
        motor_channel2: int = 2,
    ) -> None:
        """Initialize CarDriver with PCA9685.

        Args:
            i2c_address: I2C address of PCA9685 (default: 0x40)
            frequency: PWM frequency in Hz (default: 50Hz)
            steer_channel: PCA9685 channel for steering servo (default: 0)
            motor_channel1: First PCA9685 channel for DC motor (default: 1)
            motor_channel2: Second PCA9685 channel for DC motor (default: 2)

        Raises:
            RuntimeError: If I2C communication fails or PCA9685 is not found
        """
        self.steer_channel = steer_channel
        self.motor_channel1 = motor_channel1
        self.motor_channel2 = motor_channel2
        self._pca9685: Optional[PCA9685] = None
        self._steering_servo: Optional[object] = None  # PCA9685 channel object
        self._dc_motor: Optional[DCMotor] = None
        self._initialized = False

        try:
            # Initialize I2C bus (SDA=GPIO2, SCL=GPIO3)
            i2c = busio.I2C(board.SCL, board.SDA)
            
            # Initialize PCA9685
            self._pca9685 = PCA9685(i2c, address=i2c_address)
            self._pca9685.frequency = frequency

            # Initialize steering servo on Channel 0
            # Store PWM channel for direct control
            self._steering_servo = self._pca9685.channels[steer_channel]

            # Initialize DC motor on Channels 1 & 2 (H-bridge)
            motor_pwm1 = self._pca9685.channels[motor_channel1]
            motor_pwm2 = self._pca9685.channels[motor_channel2]
            self._dc_motor = DCMotor(motor_pwm1, motor_pwm2)

            self._initialized = True
            logger.info(
                f"CarDriver initialized: PCA9685@0x{i2c_address:02x}, "
                f"freq={frequency}Hz, steer=ch{steer_channel}, "
                f"motor=ch{motor_channel1}&{motor_channel2}"
            )
        except Exception as exc:
            logger.error(f"Failed to initialize CarDriver: {exc}")
            self.cleanup()
            raise RuntimeError(f"CarDriver initialization failed: {exc}") from exc

    def set_steering(self, value: float) -> None:
        """Set steering angle.

        Args:
            value: Steering value in range [-1.0, +1.0]
                -1.0: Maximum left
                0.0: Center
                +1.0: Maximum right

        Raises:
            RuntimeError: If driver is not initialized
        """
        if not self._initialized or self._steering_servo is None:
            raise RuntimeError("CarDriver not initialized")

        # Clamp value to valid range
        value = max(-1.0, min(1.0, value))

        try:
            # Map value to pulse width in microseconds
            if value >= 0:
                # Right turn: 0.0 -> center, +1.0 -> right max
                pulse_width_us = int(
                    self.STEER_CENTER_US
                    + (self.STEER_RIGHT_US - self.STEER_CENTER_US) * value
                )
            else:
                # Left turn: -1.0 -> left max, 0.0 -> center
                pulse_width_us = int(
                    self.STEER_CENTER_US
                    + (self.STEER_CENTER_US - self.STEER_LEFT_US) * value
                )
            
            # Convert pulse width to duty cycle
            # PCA9685 duty_cycle is 16-bit (0-65535) representing the fraction of the period
            # For 50Hz: period = 20ms = 20000us
            # duty_cycle = (pulse_width_us / period_us) * 65535
            period_us = 1_000_000 // self._pca9685.frequency  # Period in microseconds
            duty_cycle = int((pulse_width_us / period_us) * 65535)
            duty_cycle = max(0, min(65535, duty_cycle))
            
            self._steering_servo.duty_cycle = duty_cycle
            logger.debug(f"Steering set: value={value:.3f}, pulse={pulse_width_us}us, duty={duty_cycle}")
        except Exception as exc:
            logger.error(f"Failed to set steering: {exc}")
            raise RuntimeError(f"Steering control failed: {exc}") from exc

    def set_throttle(self, value: float) -> None:
        """Set motor throttle.

        Args:
            value: Throttle value in range [-1.0, +1.0]
                -1.0: Maximum reverse
                0.0: Stop (coasting or brake)
                +1.0: Maximum forward

        Raises:
            RuntimeError: If driver is not initialized
        """
        if not self._initialized or self._dc_motor is None:
            raise RuntimeError("CarDriver not initialized")

        # Clamp value to valid range
        value = max(-1.0, min(1.0, value))

        try:
            if value == 0.0:
                # Stop: use None for coasting (or 0 for brake)
                # Using None for coasting as default
                self._dc_motor.throttle = None
                logger.debug("Throttle set: stop (coasting)")
            else:
                # Forward (positive) or reverse (negative)
                self._dc_motor.throttle = value
                direction = "forward" if value > 0 else "reverse"
                logger.debug(f"Throttle set: {direction}, value={value:.3f}")
        except Exception as exc:
            logger.error(f"Failed to set throttle: {exc}")
            raise RuntimeError(f"Throttle control failed: {exc}") from exc

    def stop(self) -> None:
        """Stop both steering and motor immediately."""
        try:
            if self._dc_motor is not None:
                self._dc_motor.throttle = None
            if self._steering_servo is not None:
                # Return to center position
                self.set_steering(0.0)
            logger.info("CarDriver stopped")
        except Exception as exc:
            logger.warning(f"Error during stop: {exc}")

    def cleanup(self) -> None:
        """Clean up resources and stop all motors."""
        try:
            self.stop()
        except Exception:
            pass

        try:
            if self._pca9685 is not None:
                # PCA9685 doesn't have explicit close, but we can deinitialize
                self._pca9685 = None
        except Exception:
            pass

        self._steering_servo = None
        self._dc_motor = None
        self._initialized = False
        logger.info("CarDriver cleaned up")

    def __del__(self) -> None:
        """Destructor: ensure motors are stopped."""
        try:
            self.cleanup()
        except Exception:
            pass

    def __enter__(self) -> CarDriver:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit: cleanup on exit."""
        self.cleanup()
