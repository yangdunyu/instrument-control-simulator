from app.simulator.laser_adapter import LaserAdapter
from app.simulator.laser_device import LaserDevice
from app.simulator.scpi_protocol import SCPIProtocol


class RecordingProtocol(SCPIProtocol):
    def __init__(self) -> None:
        super().__init__(LaserDevice())
        self.commands: list[str] = []

    def send(self, command: str) -> str:
        self.commands.append(command)
        return super().send(command)


def test_adapter_maps_power_on_to_scpi() -> None:
    protocol = RecordingProtocol()
    adapter = LaserAdapter(protocol)

    result = adapter.power_on()

    assert protocol.commands[-1] == "OUTP ON"
    assert result["outputEnabled"] is True


def test_adapter_maps_set_power_to_scpi() -> None:
    protocol = RecordingProtocol()
    adapter = LaserAdapter(protocol)

    result = adapter.set_power(-10)

    assert protocol.commands[-1] == "SOUR:POW -10"
    assert result["powerDbm"] == -10.0


def test_protocol_sends_raw_command_to_device() -> None:
    device = LaserDevice()
    protocol = SCPIProtocol(device)

    response = protocol.send("*IDN?")

    assert response.startswith("Quantifi-Sim")
