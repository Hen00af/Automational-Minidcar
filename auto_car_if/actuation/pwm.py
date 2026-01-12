"""pigpio-based Actuation implementation for ESC + servo.

Note: Update pulse widths with measured values on your vehicle.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Optional

try:
    import pigpio
except ImportError as exc:  # pragma: no cover - runtime dependency
    raise ImportError("pigpio is required for PWMActuation (install and run pigpiod)") from exc

from ..domain.command import Command, DriveMode
from ..domain.actuation import ActuationCalibration, Telemetry, ActuationStatus
from ..interfaces.protocols import Actuation


DEFAULT_CALIB = ActuationCalibration(
    steer_center_us=1500,
    steer_left_us=1000,   # steer=+1.0
    steer_right_us=2000,  # steer=-1.0
    throttle_stop_us=1500,
    throttle_max_us=2000,
    steer_limit=1.0,
    throttle_limit=1.0,
)


class PWMActuation(Actuation):
    def __init__(
        self,
        gpio_steer: int = 14,
        gpio_throttle: int = 13,
        calib: ActuationCalibration = DEFAULT_CALIB,
    ) -> None:
        self.gpio_steer = gpio_steer
        self.gpio_throttle = gpio_throttle
        self.calib = calib
        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError("pigpio daemon not running; start with `sudo pigpiod`")

    def configure(self, calib: ActuationCalibration) -> None:
        self.calib = calib

    def _map_steer(self, steer: float) -> int:
        steer = max(-self.calib.steer_limit, min(self.calib.steer_limit, steer))
        if steer >= 0:
            return int(self.calib.steer_center_us + (self.calib.steer_left_us - self.calib.steer_center_us) * steer)
        return int(self.calib.steer_center_us + (self.calib.steer_center_us - self.calib.steer_right_us) * steer)

    def _map_throttle(self, throttle: float) -> int:
        # Clamp throttle to valid range
        # Note: Negative throttle (reverse) is not supported by this ESC-based implementation.
        # For reverse support, extend ActuationCalibration with throttle_min_us parameter.
        if throttle < 0.0:
            import warnings
            warnings.warn(
                f"Negative throttle ({throttle}) not supported by PWMActuation. "
                "Clamping to 0.0. Use CarDriver for reverse support.",
                UserWarning,
            )
            throttle = 0.0
        throttle = max(0.0, min(self.calib.throttle_limit, throttle))
        return int(self.calib.throttle_stop_us + (self.calib.throttle_max_us - self.calib.throttle_stop_us) * throttle)

    def apply(self, command: Command) -> Telemetry:
        if command.mode != DriveMode.RUN:
            return self.stop("mode_stop")

        steer_us = self._map_steer(command.steer)
        throttle_us = self._map_throttle(command.throttle)

        try:
            self.pi.set_servo_pulsewidth(self.gpio_steer, steer_us)
            self.pi.set_servo_pulsewidth(self.gpio_throttle, throttle_us)
            status = ActuationStatus.OK
            message: Optional[str] = None
        except Exception as exc:  # pragma: no cover - hardware interaction
            status = ActuationStatus.DRIVER_ERROR
            message = str(exc)

        return Telemetry(
            frame_id=command.frame_id,
            t_capture_sec=command.t_capture_sec,
            status=status,
            applied_steer=command.steer,
            applied_throttle=command.throttle,
            steer_pwm_us=steer_us,
            throttle_pwm_us=throttle_us,
            message=message,
        )

    def stop(self, reason: str = "stop") -> Telemetry:
        steer_us = self.calib.steer_center_us
        throttle_us = self.calib.throttle_stop_us
        try:
            self.pi.set_servo_pulsewidth(self.gpio_steer, steer_us)
            self.pi.set_servo_pulsewidth(self.gpio_throttle, throttle_us)
        except Exception:
            pass  # best effort

        return Telemetry(
            frame_id=0,
            t_capture_sec=0.0,
            status=ActuationStatus.STOPPED,
            applied_steer=0.0,
            applied_throttle=0.0,
            steer_pwm_us=steer_us,
            throttle_pwm_us=throttle_us,
            message=reason,
        )

    def close(self) -> None:
        try:
            self.stop("close")
        finally:
            if self.pi is not None:
                self.pi.stop()
                self.pi = None

    def __del__(self):  # pragma: no cover - best-effort cleanup
        try:
            self.close()
        except Exception:
            pass
