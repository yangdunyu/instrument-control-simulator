import random
import time

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


class LaserInstrumentSimulator(InstrumentBase):
    """Simulates a Quantifi-style optical laser instrument.

    Supports 10 SCPI-like commands, optional random error/delay
    injection to mimic real instrument behaviour.
    """

    def __init__(self, simulate_errors: bool = True) -> None:
        self.state = InstrumentState()
        self._simulate_errors = simulate_errors

    # ------------------------------------------------------------------
    # InstrumentBase interface
    # ------------------------------------------------------------------

    def handle_command(self, cmd: str) -> str:
        cmd = cmd.strip().upper()

        if self._simulate_errors:
            time.sleep(random.uniform(0.05, 0.3))
            if random.random() < 0.05:
                self.state.last_error = "TIMEOUT"
                return "ERROR:TIMEOUT"

        # *IDN?
        if cmd == "*IDN?":
            return (
                f"Quantifi-Sim,{self.state.model},"
                f"{self.state.serial},{self.state.firmware_version}"
            )

        # SYST:VERS?
        if cmd == "SYST:VERS?":
            return self.state.firmware_version

        # SOUR:POW <value>
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

        # SOUR:POW?
        if cmd == "SOUR:POW?":
            return f"{self.state.power_dbm:.2f}"

        # OUTP ON / OUTP OFF
        if cmd == "OUTP ON":
            self.state.output_enabled = True
            return "OK"

        if cmd == "OUTP OFF":
            self.state.output_enabled = False
            return "OK"

        # OUTP?
        if cmd == "OUTP?":
            return "1" if self.state.output_enabled else "0"

        # MEAS:POW?
        if cmd == "MEAS:POW?":
            if not self.state.output_enabled:
                self.state.last_error = "OUTPUT_DISABLED"
                return "ERROR:OUTPUT_DISABLED"
            noise = random.uniform(-0.05, 0.05) if self._simulate_errors else 0.0
            return f"{self.state.power_dbm + noise:.2f}"

        # SYST:ERR?
        if cmd == "SYST:ERR?":
            return self.state.last_error

        # *RST
        if cmd == "*RST":
            self.reset()
            return "OK"

        self.state.last_error = "UNKNOWN_COMMAND"
        return "ERROR:UNKNOWN_COMMAND"

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
