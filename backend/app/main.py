import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    CommandRequest,
    CommandResponse,
    OutputRequest,
    PowerRequest,
    ScriptRequest,
    ScriptResponse,
    ScriptStepResult,
)
from .simulator.firmware import FirmwareManager
from .simulator.laser_api import InstrumentCommandError, LaserInstrumentAPI
from .simulator.laser_simulator import LaserInstrumentSimulator

app = FastAPI(
    title="Instrument Control Simulator",
    description="Simulates SCPI-based optical test instruments.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Instrument registry  (discovery endpoint iterates this dict)
# ---------------------------------------------------------------------------
_simulate_errors = os.environ.get("SIMULATE_ERRORS", "true").lower() == "true"

laser = LaserInstrumentSimulator(simulate_errors=_simulate_errors)

INSTRUMENTS: dict[str, LaserInstrumentSimulator] = {
    "laser-001": laser,
}

_firmware_managers: dict[str, FirmwareManager] = {
    "laser-001": FirmwareManager(laser.state),
}

_laser_apis: dict[str, LaserInstrumentAPI] = {
    "laser-001": LaserInstrumentAPI(laser),
}


def _get_instrument(instrument_id: str) -> LaserInstrumentSimulator:
    if instrument_id not in INSTRUMENTS:
        raise HTTPException(status_code=404, detail="Instrument not found")
    return INSTRUMENTS[instrument_id]


def _get_firmware_manager(instrument_id: str) -> FirmwareManager:
    if instrument_id not in _firmware_managers:
        raise HTTPException(status_code=404, detail="Instrument not found")
    return _firmware_managers[instrument_id]


def _get_laser_api(instrument_id: str) -> LaserInstrumentAPI:
    if instrument_id not in _laser_apis:
        raise HTTPException(status_code=404, detail="Instrument not found")
    return _laser_apis[instrument_id]


def _require_connected(inst: LaserInstrumentSimulator) -> None:
    if not inst.state.connected:
        raise HTTPException(status_code=400, detail="Instrument not connected")


def _run_semantic_call(func):
    try:
        return func()
    except InstrumentCommandError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/api/instruments")
def list_instruments() -> list[dict]:
    """Discover all available instruments."""
    return [
        {
            "id": iid,
            "model": inst.state.model,
            "serial": inst.state.serial,
            "firmwareVersion": inst.state.firmware_version,
            "status": "connected" if inst.state.connected else "available",
        }
        for iid, inst in INSTRUMENTS.items()
    ]


@app.post("/api/instruments/{instrument_id}/connect")
def connect_instrument(instrument_id: str) -> dict:
    inst = _get_instrument(instrument_id)
    inst.state.connected = True
    identity = inst.handle_command("*IDN?")
    return {"status": "connected", "identity": identity}


@app.post("/api/instruments/{instrument_id}/disconnect")
def disconnect_instrument(instrument_id: str) -> dict:
    inst = _get_instrument(instrument_id)
    inst.state.connected = False
    return {"status": "disconnected"}


@app.get("/api/instruments/{instrument_id}/status")
def get_status(instrument_id: str) -> dict:
    inst = _get_instrument(instrument_id)
    return inst.get_status()


@app.post("/api/instruments/{instrument_id}/command")
def send_command(instrument_id: str, req: CommandRequest) -> CommandResponse:
    inst = _get_instrument(instrument_id)
    _require_connected(inst)
    response = inst.handle_command(req.command)
    return CommandResponse(command=req.command, response=response)


@app.post("/api/instruments/{instrument_id}/output")
def set_output(instrument_id: str, req: OutputRequest) -> dict:
    inst = _get_instrument(instrument_id)
    _require_connected(inst)
    api = _get_laser_api(instrument_id)
    return _run_semantic_call(lambda: api.set_output(req.enabled))


@app.post("/api/instruments/{instrument_id}/power")
def set_power(instrument_id: str, req: PowerRequest) -> dict:
    inst = _get_instrument(instrument_id)
    _require_connected(inst)
    api = _get_laser_api(instrument_id)
    return _run_semantic_call(lambda: api.set_power(req.dbm))


@app.get("/api/instruments/{instrument_id}/power")
def read_power(instrument_id: str) -> dict:
    inst = _get_instrument(instrument_id)
    _require_connected(inst)
    api = _get_laser_api(instrument_id)
    return _run_semantic_call(api.read_power)


@app.post("/api/instruments/{instrument_id}/script")
def run_script(instrument_id: str, req: ScriptRequest) -> ScriptResponse:
    """Run a newline-delimited SCPI script and return a pass/fail report."""
    inst = _get_instrument(instrument_id)
    _require_connected(inst)

    commands = [
        (idx, line.strip())
        for idx, line in enumerate(req.script.splitlines(), start=1)
        if line.strip() and not line.strip().startswith("#")
    ]
    if not commands:
        raise HTTPException(status_code=400, detail="Script has no commands")
    if len(commands) > 50:
        raise HTTPException(status_code=400, detail="Script exceeds 50 commands")

    results: list[ScriptStepResult] = []
    failed = 0
    for line_no, command in commands:
        response = inst.handle_command(command)
        passed = not response.startswith("ERROR")
        if not passed:
            failed += 1
        results.append(
            ScriptStepResult(
                line=line_no,
                command=command,
                response=response,
                passed=passed,
            )
        )

    return ScriptResponse(
        passed=failed == 0,
        total=len(results),
        failed=failed,
        results=results,
    )


@app.post("/api/instruments/{instrument_id}/firmware/upgrade")
def start_firmware_upgrade(instrument_id: str) -> dict:
    _get_instrument(instrument_id)
    fm = _get_firmware_manager(instrument_id)
    if not fm.start_update():
        raise HTTPException(status_code=409, detail="Firmware upgrade already in progress")
    return {"status": "started"}


@app.get("/api/instruments/{instrument_id}/firmware/status")
def get_firmware_status(instrument_id: str) -> dict:
    _get_instrument(instrument_id)
    fm = _get_firmware_manager(instrument_id)
    return fm.get_status()
