"""Unit tests for the SCPI command parser.

Each test covers one command in the supported command set.
Simulator is created with simulate_errors=False for deterministic results.
"""

import pytest

from app.simulator.laser_simulator import LaserInstrumentSimulator


@pytest.fixture
def sim() -> LaserInstrumentSimulator:
    return LaserInstrumentSimulator(simulate_errors=False)


def test_idn(sim: LaserInstrumentSimulator) -> None:
    resp = sim.handle_command("*IDN?")
    assert resp.startswith("Quantifi-Sim")
    assert "QP-LASER-SIM" in resp
    assert "SIM-001" in resp


def test_syst_vers(sim: LaserInstrumentSimulator) -> None:
    assert sim.handle_command("SYST:VERS?") == "1.0.0"


def test_sour_pow_set(sim: LaserInstrumentSimulator) -> None:
    assert sim.handle_command("SOUR:POW -10") == "OK"
    assert sim.state.power_dbm == -10.0


def test_sour_pow_query(sim: LaserInstrumentSimulator) -> None:
    sim.handle_command("SOUR:POW -10")
    assert float(sim.handle_command("SOUR:POW?")) == -10.0


def test_sour_pow_out_of_range(sim: LaserInstrumentSimulator) -> None:
    assert sim.handle_command("SOUR:POW 100") == "ERROR:POWER_OUT_OF_RANGE"
    assert sim.handle_command("SOUR:POW -99") == "ERROR:POWER_OUT_OF_RANGE"


def test_outp_on(sim: LaserInstrumentSimulator) -> None:
    assert sim.handle_command("OUTP ON") == "OK"
    assert sim.state.output_enabled is True


def test_outp_off(sim: LaserInstrumentSimulator) -> None:
    sim.handle_command("OUTP ON")
    assert sim.handle_command("OUTP OFF") == "OK"
    assert sim.state.output_enabled is False


def test_outp_query(sim: LaserInstrumentSimulator) -> None:
    assert sim.handle_command("OUTP?") == "0"
    sim.handle_command("OUTP ON")
    assert sim.handle_command("OUTP?") == "1"


def test_meas_pow_requires_output(sim: LaserInstrumentSimulator) -> None:
    assert sim.handle_command("MEAS:POW?") == "ERROR:OUTPUT_DISABLED"


def test_meas_pow_returns_value(sim: LaserInstrumentSimulator) -> None:
    sim.handle_command("SOUR:POW -10")
    sim.handle_command("OUTP ON")
    resp = sim.handle_command("MEAS:POW?")
    assert float(resp) == pytest.approx(-10.0, abs=0.1)


def test_syst_err(sim: LaserInstrumentSimulator) -> None:
    sim.handle_command("SOUR:POW 999")  # triggers error
    assert sim.handle_command("SYST:ERR?") == "POWER_OUT_OF_RANGE"


def test_rst(sim: LaserInstrumentSimulator) -> None:
    sim.handle_command("SOUR:POW -20")
    sim.handle_command("OUTP ON")
    assert sim.handle_command("*RST") == "OK"
    assert sim.state.power_dbm == 0.0
    assert sim.state.output_enabled is False
