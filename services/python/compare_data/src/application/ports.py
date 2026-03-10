"""Port interfaces for the application layer."""
from abc import ABC, abstractmethod

from src.domain.models import EquipmentRecord


class EquipmentDataPort(ABC):
    """Data source port (adapter pattern)."""

    @abstractmethod
    def load_records(self) -> list[EquipmentRecord]:
        """Load equipment records."""
        ...

    @abstractmethod
    def get_record_count(self) -> int:
        """Return record count."""
        ...
