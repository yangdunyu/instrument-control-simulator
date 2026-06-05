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
from .simulator.instrument_service import (
    InstrumentCommandError,
    InstrumentNotConnectedError,
    InstrumentNotFoundError,
    InstrumentService,
)

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

service = InstrumentService()


def _map_service_error(exc: Exception) -> HTTPException:
    if isinstance(exc, InstrumentNotFoundError):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, (InstrumentNotConnectedError, InstrumentCommandError, ValueError)):
        return HTTPException(status_code=400, detail=str(exc))
    return HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/instruments")
def list_instruments() -> list[dict]:
    return service.list_instruments()


@app.post("/api/instruments/{instrument_id}/connect")
def connect_instrument(instrument_id: str) -> dict:
    try:
        return service.connect(instrument_id)
    except Exception as exc:
        raise _map_service_error(exc) from exc


@app.post("/api/instruments/{instrument_id}/disconnect")
def disconnect_instrument(instrument_id: str) -> dict:
    try:
        return service.disconnect(instrument_id)
    except Exception as exc:
        raise _map_service_error(exc) from exc


@app.get("/api/instruments/{instrument_id}/status")
def get_status(instrument_id: str) -> dict:
    try:
        return service.get_status(instrument_id)
    except Exception as exc:
        raise _map_service_error(exc) from exc


@app.post("/api/instruments/{instrument_id}/command")
def send_command(instrument_id: str, req: CommandRequest) -> CommandResponse:
    try:
        response = service.send_raw(instrument_id, req.command)
        return CommandResponse(command=req.command, response=response)
    except Exception as exc:
        raise _map_service_error(exc) from exc


@app.post("/api/instruments/{instrument_id}/output")
def set_output(instrument_id: str, req: OutputRequest) -> dict:
    try:
        return service.power_on(instrument_id) if req.enabled else service.power_off(instrument_id)
    except Exception as exc:
        raise _map_service_error(exc) from exc


@app.post("/api/instruments/{instrument_id}/power")
def set_power(instrument_id: str, req: PowerRequest) -> dict:
    try:
        return service.set_power(instrument_id, req.dbm)
    except Exception as exc:
        raise _map_service_error(exc) from exc


@app.get("/api/instruments/{instrument_id}/power")
def read_power(instrument_id: str) -> dict:
    try:
        return service.measure(instrument_id)
    except Exception as exc:
        raise _map_service_error(exc) from exc


@app.post("/api/instruments/{instrument_id}/script")
def run_script(instrument_id: str, req: ScriptRequest) -> ScriptResponse:
    try:
        raw_results = service.run_script(instrument_id, req.script)
    except Exception as exc:
        raise _map_service_error(exc) from exc

    results: list[ScriptStepResult] = []
    failed = 0
    for line_no, command, response in raw_results:
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
    try:
        if not service.start_firmware_upgrade(instrument_id):
            raise HTTPException(status_code=409, detail="Firmware upgrade already in progress")
        return {"status": "started"}
    except HTTPException:
        raise
    except Exception as exc:
        raise _map_service_error(exc) from exc


@app.get("/api/instruments/{instrument_id}/firmware/status")
def get_firmware_status(instrument_id: str) -> dict:
    try:
        return service.get_firmware_status(instrument_id)
    except Exception as exc:
        raise _map_service_error(exc) from exc
