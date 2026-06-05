"""Integration tests for the REST API endpoints.

Uses FastAPI's TestClient (httpx-backed).
conftest.py sets SIMULATE_ERRORS=false before app import.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import INSTRUMENTS, _firmware_managers, app

client = TestClient(app)
LASER_ID = "laser-001"


@pytest.fixture(autouse=True)
def reset_state() -> None:
    """Reset instrument and firmware state before each test."""
    inst = INSTRUMENTS[LASER_ID]
    inst.reset()
    inst.state.connected = False
    fm = _firmware_managers[LASER_ID]
    fm.update_state = "idle"
    fm.progress = 0


def test_list_instruments() -> None:
    resp = client.get("/api/instruments")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == LASER_ID
    assert data[0]["status"] == "available"


def test_connect() -> None:
    resp = client.post(f"/api/instruments/{LASER_ID}/connect")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "connected"
    assert "Quantifi-Sim" in body["identity"]


def test_get_status_after_connect() -> None:
    client.post(f"/api/instruments/{LASER_ID}/connect")
    resp = client.get(f"/api/instruments/{LASER_ID}/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["connected"] is True
    assert "powerDbm" in data


def test_send_command() -> None:
    client.post(f"/api/instruments/{LASER_ID}/connect")
    resp = client.post(
        f"/api/instruments/{LASER_ID}/command",
        json={"command": "OUTP ON"},
    )
    assert resp.status_code == 200
    assert resp.json()["response"] == "OK"


def test_command_requires_connection() -> None:
    # instrument is disconnected (reset_state fixture)
    resp = client.post(
        f"/api/instruments/{LASER_ID}/command",
        json={"command": "*IDN?"},
    )
    assert resp.status_code == 400


def test_firmware_upgrade_starts() -> None:
    client.post(f"/api/instruments/{LASER_ID}/connect")
    resp = client.post(f"/api/instruments/{LASER_ID}/firmware/upgrade")
    assert resp.status_code == 200
    assert resp.json()["status"] == "started"

    status_resp = client.get(f"/api/instruments/{LASER_ID}/firmware/status")
    assert status_resp.status_code == 200
    assert status_resp.json()["state"] != "idle"


def test_structured_output_endpoint() -> None:
    client.post(f"/api/instruments/{LASER_ID}/connect")
    resp = client.post(
        f"/api/instruments/{LASER_ID}/output",
        json={"enabled": True},
    )
    assert resp.status_code == 200
    assert resp.json()["outputEnabled"] is True


def test_structured_power_endpoint() -> None:
    client.post(f"/api/instruments/{LASER_ID}/connect")
    resp = client.post(
        f"/api/instruments/{LASER_ID}/power",
        json={"dbm": -10},
    )
    assert resp.status_code == 200
    assert resp.json()["powerDbm"] == -10.0


def test_structured_read_power_requires_output() -> None:
    client.post(f"/api/instruments/{LASER_ID}/connect")
    resp = client.get(f"/api/instruments/{LASER_ID}/power")
    assert resp.status_code == 400
    assert resp.json()["detail"] == "ERROR:OUTPUT_DISABLED"


def test_structured_read_power_returns_measurement() -> None:
    client.post(f"/api/instruments/{LASER_ID}/connect")
    client.post(f"/api/instruments/{LASER_ID}/power", json={"dbm": -12})
    client.post(f"/api/instruments/{LASER_ID}/output", json={"enabled": True})

    resp = client.get(f"/api/instruments/{LASER_ID}/power")
    assert resp.status_code == 200
    assert resp.json()["powerDbm"] == -12.0


def test_script_runner_returns_pass_fail_report() -> None:
    client.post(f"/api/instruments/{LASER_ID}/connect")
    resp = client.post(
        f"/api/instruments/{LASER_ID}/script",
        json={"script": "# smoke test\nSOUR:POW -10\nOUTP ON\nMEAS:POW?\nBAD:CMD?"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["passed"] is False
    assert body["total"] == 4
    assert body["failed"] == 1
    assert body["results"][-1]["response"] == "ERROR:UNKNOWN_COMMAND"


def test_script_runner_requires_connection() -> None:
    resp = client.post(
        f"/api/instruments/{LASER_ID}/script",
        json={"script": "*IDN?"},
    )
    assert resp.status_code == 400
