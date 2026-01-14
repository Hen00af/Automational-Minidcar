#!/usr/bin/env python3
"""Sensor-based entrypoint using ultrasonic sensor + pigpio.

Safety: run with wheels lifted for first test. Ctrl+C to stop.
"""
from __future__ import annotations

import time

from ..orchestrator import Orchestrator
from ..sensor import UltrasonicSensor
from ..perception import SensorBasedPerception
from ..decision import SimpleDecision
from ..actuation import PWMActuation


def main() -> None:
    sensor = UltrasonicSensor(gpio_trigger=23, gpio_echo=24)
    perception = SensorBasedPerception(
        safe_distance_mm=200.0,
        critical_distance_mm=100.0,
        front_sensor_id="front",
    )
    decision = SimpleDecision()
    actuation = PWMActuation()
    orch = Orchestrator(
        sensor=sensor,
        sensor_perception=perception,
        decision=decision,
        actuation=actuation,
    )

    input("[SAFE] Lift the wheels, then press Enter to start. Ctrl+C to stop. > ")
    try:
        orch.run_loop()
    except KeyboardInterrupt:
        actuation.stop("keyboard_interrupt")
    finally:
        actuation.close()
        time.sleep(0.3)


if __name__ == "__main__":
    main()
