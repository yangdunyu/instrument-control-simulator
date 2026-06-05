from .laser_simulator import LaserInstrumentSimulator


class InstrumentCommandError(Exception):
    """Raised when a semantic API call maps to a failed SCPI command."""


class LaserInstrumentAPI:
    """High-level instrument API wrapping raw SCPI commands.

    This layer lets UI/API clients use semantic operations like
    set_power() and enable_output() while the simulator still speaks SCPI.
    """

    def __init__(self, simulator: LaserInstrumentSimulator) -> None:
        self._sim = simulator

    def set_power(self, dbm: float) -> dict:
        response = self._checked(f"SOUR:POW {dbm}")
        return {"response": response, "powerDbm": self._sim.state.power_dbm}

    def set_output(self, enabled: bool) -> dict:
        response = self._checked("OUTP ON" if enabled else "OUTP OFF")
        return {"response": response, "outputEnabled": self._sim.state.output_enabled}

    def read_power(self) -> dict:
        response = self._checked("MEAS:POW?")
        return {"powerDbm": float(response)}

    def _checked(self, command: str) -> str:
        response = self._sim.handle_command(command)
        if response.startswith("ERROR"):
            raise InstrumentCommandError(response)
        return response
