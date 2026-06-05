from abc import ABC, abstractmethod


class InstrumentBase(ABC):
    """Abstract base class for all simulated instruments.

    Defines the contract that every instrument must implement,
    enabling the framework to handle multiple instrument types
    through a single, uniform interface.
    """

    @abstractmethod
    def handle_command(self, cmd: str) -> str:
        """Process a SCPI-like command and return the response string."""
        ...

    @abstractmethod
    def get_status(self) -> dict:
        """Return current instrument state as a serialisable dict."""
        ...

    @abstractmethod
    def reset(self) -> None:
        """Reset all instrument state to factory defaults."""
        ...
