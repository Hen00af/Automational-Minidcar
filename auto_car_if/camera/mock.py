"""Mock PiCameraCV for local development (no hardware required).
"""
import numpy as np


import time

class PiCameraCV:
    def __init__(self, width=320, height=240, device=0):
        self.width = width
        self.height = height
        self.device = device
        self._frame = np.zeros((height, width, 3), dtype=np.uint8)
        self._open = True

    def read(self):
        # Return a dummy black frame
        return True, self._frame.copy()

    def frames(self):
        # Infinite generator of dummy frames with .image, .frame_id, and .t_capture_sec attributes
        import time as _time
        class DummyFrame:
            def __init__(self, arr, frame_id, t_capture_sec):
                self.image = arr
                self.frame_id = frame_id
                self.t_capture_sec = t_capture_sec
        frame_id = 0
        while self._open:
            yield DummyFrame(self._frame.copy(), frame_id, _time.time())
            frame_id += 1
            _time.sleep(0.05)

    def close(self):
        self._open = False

    def isOpened(self):
        return self._open
