from .scpi_protocol import SCPIProtocol


class InstrumentCommandError(Exception):
    """Raised when an adapter call maps to a failed SCPI command."""


class LaserAdapter:
    """Adapter layer: maps common laser actions to SCPI commands."""

    def __init__(self, protocol: SCPIProtocol) -> None:
        self._protocol = protocol

    @property
    def device(self):
        return self._protocol.device

    def identity(self) -> str:
        return self._checked("*IDN?")

    def power_on(self) -> dict:
        response = self._checked("OUTP ON")
        return {"response": response, "outputEnabled": True}

    def power_off(self) -> dict:
        response = self._checked("OUTP OFF")
        return {"response": response, "outputEnabled": False}

    def set_power(self, dbm: float) -> dict:
        response = self._checked(f"SOUR:POW {dbm}")
        return {"response": response, "powerDbm": self.device.state.power_dbm}

    def measure(self) -> dict:
        response = self._checked("MEAS:POW?")
        return {"powerDbm": float(response)}

    def send_raw(self, command: str) -> str:
        return self._protocol.send(command)

    def _checked(self, command: str) -> str:
        response = self._protocol.send(command)
        if response.startswith("ERROR"):
            raise InstrumentCommandError(response)
        return response
