#!/usr/bin/env python3
"""Real-device entrypoint using Pi Camera + pigpio.

Safety: run with wheels lifted for first test. Ctrl+C to stop.
"""
from __future__ import annotations

import time

from ..orchestrator import Orchestrator
from ..camera import PiCameraCV
from ..perception import LinePerception
from ..decision import SimpleDecision
from ..actuation import PWMActuation


def main() -> None:
    cam = PiCameraCV(width=320, height=240)
    perception = LinePerception()
    decision = SimpleDecision()
    actuation = PWMActuation()
    orch = Orchestrator(cam, perception, decision, actuation)

    input("[SAFE] Lift the wheels, then press Enter to start. Ctrl+C to stop. > ")
    try:
        orch.run_loop()
    except KeyboardInterrupt:
        actuation.stop("keyboard_interrupt")
    finally:
        actuation.close()
        cam.close()
        time.sleep(0.3)


if __name__ == "__main__":
    main()

