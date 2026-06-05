from pydantic import BaseModel


class CommandRequest(BaseModel):
    command: str


class CommandResponse(BaseModel):
    command: str
    response: str


class OutputRequest(BaseModel):
    enabled: bool


class PowerRequest(BaseModel):
    dbm: float


class ScriptRequest(BaseModel):
    script: str


class ScriptStepResult(BaseModel):
    line: int
    command: str
    response: str
    passed: bool


class ScriptResponse(BaseModel):
    passed: bool
    total: int
    failed: int
    results: list[ScriptStepResult]


class InstrumentInfo(BaseModel):
    id: str
    model: str
    serial: str
    firmware_version: str
    status: str
