"""Unit tests for the SCPI command parser.

Each test covers one command in the supported command set.
LaserDevice owns state and executes raw SCPI commands deterministically.
"""

import pytest

from app.simulator.laser_device import LaserDevice


@pytest.fixture
def sim() -> LaserDevice:
    return LaserDevice()


def test_idn(sim: LaserDevice) -> None:
    resp = sim.execute("*IDN?")
    assert resp.startswith("Quantifi-Sim")
    assert "QP-LASER-SIM" in resp
    assert "SIM-001" in resp


def test_syst_vers(sim: LaserDevice) -> None:
    assert sim.execute("SYST:VERS?") == "1.0.0"


def test_sour_pow_set(sim: LaserDevice) -> None:
    assert sim.execute("SOUR:POW -10") == "OK"
    assert sim.state.power_dbm == -10.0


def test_sour_pow_query(sim: LaserDevice) -> None:
    sim.execute("SOUR:POW -10")
    assert float(sim.execute("SOUR:POW?")) == -10.0


def test_sour_pow_out_of_range(sim: LaserDevice) -> None:
    assert sim.execute("SOUR:POW 100") == "ERROR:POWER_OUT_OF_RANGE"
    assert sim.execute("SOUR:POW -99") == "ERROR:POWER_OUT_OF_RANGE"


def test_outp_on(sim: LaserDevice) -> None:
    assert sim.execute("OUTP ON") == "OK"
    assert sim.state.output_enabled is True


def test_outp_off(sim: LaserDevice) -> None:
    sim.execute("OUTP ON")
    assert sim.execute("OUTP OFF") == "OK"
    assert sim.state.output_enabled is False


def test_outp_query(sim: LaserDevice) -> None:
    assert sim.execute("OUTP?") == "0"
    sim.execute("OUTP ON")
    assert sim.execute("OUTP?") == "1"


def test_meas_pow_requires_output(sim: LaserDevice) -> None:
    assert sim.execute("MEAS:POW?") == "ERROR:OUTPUT_DISABLED"


def test_meas_pow_returns_value(sim: LaserDevice) -> None:
    sim.execute("SOUR:POW -10")
    sim.execute("OUTP ON")
    resp = sim.execute("MEAS:POW?")
    assert float(resp) == pytest.approx(-10.0, abs=0.1)


def test_syst_err(sim: LaserDevice) -> None:
    sim.execute("SOUR:POW 999")  # triggers error
    assert sim.execute("SYST:ERR?") == "POWER_OUT_OF_RANGE"


def test_rst(sim: LaserDevice) -> None:
    sim.execute("SOUR:POW -20")
    sim.execute("OUTP ON")
    assert sim.execute("*RST") == "OK"
    assert sim.state.power_dbm == 0.0
    assert sim.state.output_enabled is False
