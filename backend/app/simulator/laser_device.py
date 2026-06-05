from .base import InstrumentBase


class InstrumentState:
    def __init__(self) -> None:
        self.model = "QP-LASER-SIM"
        self.serial = "SIM-001"
        self.firmware_version = "1.0.0"
        self.connected = False
        self.output_enabled = False
        self.power_dbm = 0.0
        self.temperature = 25.0
        self.last_error = "No error"


class LaserDevice(InstrumentBase):
    """Device layer: executes SCPI commands and owns instrument state."""

    def __init__(self) -> None:
        self.state = InstrumentState()

    def execute(self, cmd: str) -> str:
        cmd = cmd.strip().upper()

        if cmd == "*IDN?":
            return (
                f"Quantifi-Sim,{self.state.model},"
                f"{self.state.serial},{self.state.firmware_version}"
            )

        if cmd == "SYST:VERS?":
            return self.state.firmware_version

        if cmd.startswith("SOUR:POW "):
            try:
                value = float(cmd.split(" ", 1)[1])
            except ValueError:
                self.state.last_error = "INVALID_PARAM"
                return "ERROR:INVALID_PARAM"
            if value < -60 or value > 10:
                self.state.last_error = "POWER_OUT_OF_RANGE"
                return "ERROR:POWER_OUT_OF_RANGE"
            self.state.power_dbm = value
            return "OK"

        if cmd == "SOUR:POW?":
            return f"{self.state.power_dbm:.2f}"

        if cmd == "OUTP ON":
            self.state.output_enabled = True
            return "OK"

        if cmd == "OUTP OFF":
            self.state.output_enabled = False
            return "OK"

        if cmd == "OUTP?":
            return "1" if self.state.output_enabled else "0"

        if cmd == "MEAS:POW?":
            if not self.state.output_enabled:
                self.state.last_error = "OUTPUT_DISABLED"
                return "ERROR:OUTPUT_DISABLED"
            return f"{self.state.power_dbm:.2f}"

        if cmd == "SYST:ERR?":
            return self.state.last_error

        if cmd == "*RST":
            self.reset()
            return "OK"

        self.state.last_error = "UNKNOWN_COMMAND"
        return "ERROR:UNKNOWN_COMMAND"

    def handle_command(self, cmd: str) -> str:
        return self.execute(cmd)

    def get_status(self) -> dict:
        return {
            "connected": self.state.connected,
            "outputEnabled": self.state.output_enabled,
            "powerDbm": self.state.power_dbm,
            "temperature": self.state.temperature,
            "firmwareVersion": self.state.firmware_version,
            "lastError": self.state.last_error,
        }

    def reset(self) -> None:
        self.state.output_enabled = False
        self.state.power_dbm = 0.0
        self.state.temperature = 25.0
        self.state.last_error = "No error"
