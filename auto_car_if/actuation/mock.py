"""Mock PWMActuation for local development (no hardware required).
"""
from ..domain.actuation import ActuationCalibration, Telemetry, ActuationStatus
from ..domain.command import Command
from ..interfaces.protocols import Actuation

DEFAULT_CALIB = ActuationCalibration(
    steer_center_us=1500,
    steer_left_us=1000,
    steer_right_us=2000,
    throttle_stop_us=1500,
    throttle_max_us=2000,
    steer_limit=1.0,
    throttle_limit=1.0,
)

class PWMActuation(Actuation):
    def __init__(self, gpio_steer=14, gpio_throttle=13, calib=DEFAULT_CALIB):
        self.gpio_steer = gpio_steer
        self.gpio_throttle = gpio_throttle
        self.calib = calib
        self._stopped = False

    def configure(self, calib: ActuationCalibration) -> None:
        self.calib = calib

    def apply(self, command: Command) -> Telemetry:
        # Just return a dummy Telemetry object
        # Note: Mock accepts negative throttle values (for reverse) but doesn't enforce limits
        return Telemetry(
            frame_id=command.frame_id,
            t_capture_sec=command.t_capture_sec,
            status=ActuationStatus.OK,
            applied_steer=command.steer,
            applied_throttle=command.throttle,
            steer_pwm_us=1500,
            throttle_pwm_us=1500 if command.throttle == 0.0 else (2000 if command.throttle > 0 else 1000),
            message="mocked apply"
        )

    def stop(self, reason: str = "stop") -> Telemetry:
        self._stopped = True
        return Telemetry(
            frame_id=0,
            t_capture_sec=0.0,
            status=ActuationStatus.STOPPED,
            applied_steer=0.0,
            applied_throttle=0.0,
            steer_pwm_us=1500,
            throttle_pwm_us=1500,
            message=reason
        )

    def close(self) -> None:
        self._stopped = True
