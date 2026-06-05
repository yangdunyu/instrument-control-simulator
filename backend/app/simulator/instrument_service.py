from .firmware import FirmwareManager
from .laser_adapter import InstrumentCommandError, LaserAdapter
from .laser_device import LaserDevice
from .scpi_protocol import SCPIProtocol


class InstrumentNotFoundError(Exception):
    pass


class InstrumentNotConnectedError(Exception):
    pass


class InstrumentService:
    """Framework layer: registry plus unified instrument business actions."""

    def __init__(self, simulate_latency: bool = False) -> None:
        device = LaserDevice()
        protocol = SCPIProtocol(device, simulate_latency=simulate_latency)
        adapter = LaserAdapter(protocol)

        self._adapters: dict[str, LaserAdapter] = {"laser-001": adapter}
        self._firmware_managers: dict[str, FirmwareManager] = {
            "laser-001": FirmwareManager(device.state)
        }

    @property
    def adapters(self) -> dict[str, LaserAdapter]:
        return self._adapters

    @property
    def firmware_managers(self) -> dict[str, FirmwareManager]:
        return self._firmware_managers

    def list_instruments(self) -> list[dict]:
        return [
            {
                "id": iid,
                "model": adapter.device.state.model,
                "serial": adapter.device.state.serial,
                "firmwareVersion": adapter.device.state.firmware_version,
                "status": "connected" if adapter.device.state.connected else "available",
            }
            for iid, adapter in self._adapters.items()
        ]

    def connect(self, instrument_id: str) -> dict:
        adapter = self._get_adapter(instrument_id)
        adapter.device.state.connected = True
        return {"status": "connected", "identity": adapter.identity()}

    def disconnect(self, instrument_id: str) -> dict:
        adapter = self._get_adapter(instrument_id)
        adapter.device.state.connected = False
        return {"status": "disconnected"}

    def get_status(self, instrument_id: str) -> dict:
        return self._get_adapter(instrument_id).device.get_status()

    def send_raw(self, instrument_id: str, command: str) -> str:
        adapter = self._get_connected_adapter(instrument_id)
        return adapter.send_raw(command)

    def power_on(self, instrument_id: str) -> dict:
        return self._get_connected_adapter(instrument_id).power_on()

    def power_off(self, instrument_id: str) -> dict:
        return self._get_connected_adapter(instrument_id).power_off()

    def set_power(self, instrument_id: str, dbm: float) -> dict:
        return self._get_connected_adapter(instrument_id).set_power(dbm)

    def measure(self, instrument_id: str) -> dict:
        return self._get_connected_adapter(instrument_id).measure()

    def run_script(self, instrument_id: str, script: str) -> list[tuple[int, str, str]]:
        adapter = self._get_connected_adapter(instrument_id)
        commands = [
            (idx, line.strip())
            for idx, line in enumerate(script.splitlines(), start=1)
            if line.strip() and not line.strip().startswith("#")
        ]
        if not commands:
            raise ValueError("Script has no commands")
        if len(commands) > 50:
            raise ValueError("Script exceeds 50 commands")
        return [(line_no, command, adapter.send_raw(command)) for line_no, command in commands]

    def start_firmware_upgrade(self, instrument_id: str) -> bool:
        self._get_adapter(instrument_id)
        return self._get_firmware_manager(instrument_id).start_update()

    def get_firmware_status(self, instrument_id: str) -> dict:
        self._get_adapter(instrument_id)
        return self._get_firmware_manager(instrument_id).get_status()

    def reset_for_tests(self, instrument_id: str) -> None:
        adapter = self._get_adapter(instrument_id)
        adapter.device.reset()
        adapter.device.state.connected = False
        fm = self._get_firmware_manager(instrument_id)
        fm.update_state = "idle"
        fm.progress = 0

    def _get_adapter(self, instrument_id: str) -> LaserAdapter:
        if instrument_id not in self._adapters:
            raise InstrumentNotFoundError("Instrument not found")
        return self._adapters[instrument_id]

    def _get_connected_adapter(self, instrument_id: str) -> LaserAdapter:
        adapter = self._get_adapter(instrument_id)
        if not adapter.device.state.connected:
            raise InstrumentNotConnectedError("Instrument not connected")
        return adapter

    def _get_firmware_manager(self, instrument_id: str) -> FirmwareManager:
        if instrument_id not in self._firmware_managers:
            raise InstrumentNotFoundError("Instrument not found")
        return self._firmware_managers[instrument_id]
