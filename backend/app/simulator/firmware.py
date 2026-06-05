import random
import threading
import time

from .laser_simulator import InstrumentState


class FirmwareManager:
    """Manages the firmware upgrade lifecycle for an instrument.

    State machine:
        idle -> uploading (20%) -> validating (40%) -> applying (80%)
             -> completed (100%)  |  failed (10% probability)
    """

    STATES = ("idle", "uploading", "validating", "applying", "completed", "failed")

    def __init__(self, state: InstrumentState) -> None:
        self._state = state
        self.update_state = "idle"
        self.progress = 0
        self._lock = threading.Lock()

    def start_update(self) -> bool:
        """Begin a firmware upgrade in a background thread.

        Returns False if an upgrade is already in progress.
        """
        with self._lock:
            if self.update_state not in ("idle", "completed", "failed"):
                return False
            self.update_state = "uploading"
            self.progress = 0

        threading.Thread(target=self._run, daemon=True).start()
        return True

    def _run(self) -> None:
        steps = [
            ("uploading", 20),
            ("validating", 40),
            ("applying", 80),
        ]
        for state, progress in steps:
            with self._lock:
                self.update_state = state
                self.progress = progress
            time.sleep(1)

        # 10% chance of failure
        if random.random() < 0.10:
            with self._lock:
                self.update_state = "failed"
                self.progress = 0
            return

        with self._lock:
            self._state.firmware_version = "1.1.0"
            self.update_state = "completed"
            self.progress = 100

    def get_status(self) -> dict:
        with self._lock:
            return {
                "state": self.update_state,
                "progress": self.progress,
                "firmwareVersion": self._state.firmware_version,
            }
