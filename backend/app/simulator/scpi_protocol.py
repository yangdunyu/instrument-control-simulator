import time

from .laser_device import LaserDevice


class SCPIProtocol:
    """Protocol layer: sends SCPI strings to a device transport.

    This demo uses an in-process simulator instead of TCP/USB/VISA, but the
    interface mirrors a real protocol layer: send a command, receive a string.
    """

    def __init__(self, device: LaserDevice, simulate_latency: bool = False) -> None:
        self._device = device
        self._simulate_latency = simulate_latency

    @property
    def device(self) -> LaserDevice:
        return self._device

    def send(self, command: str) -> str:
        if self._simulate_latency:
            time.sleep(0.05)
        return self._device.execute(command)
