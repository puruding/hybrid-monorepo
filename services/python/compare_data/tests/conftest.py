"""Common test fixtures."""
import csv
from collections.abc import Generator
from pathlib import Path

import pytest
from src.domain.models import EquipmentRecord


@pytest.fixture
def sample_source_records() -> list[EquipmentRecord]:
    """Sample source records for testing."""
    return [
        EquipmentRecord(serial_number="SN001", product_name="FortiGate 100F"),
        EquipmentRecord(serial_number="SN002", product_name="Cisco ASA 5506"),
        EquipmentRecord(serial_number="SN003", product_name="Palo Alto PA-220"),
    ]


@pytest.fixture
def sample_target_records() -> list[EquipmentRecord]:
    """Sample target records for testing."""
    return [
        EquipmentRecord(serial_number="SN001", product_name="FortiGate 100F"),
        EquipmentRecord(serial_number="SN002", product_name="Cisco ASA 5505"),  # Name mismatch
        EquipmentRecord(serial_number="SN004", product_name="Juniper SRX300"),  # Target only
    ]


@pytest.fixture
def sample_csv_file(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a sample CSV file for testing."""
    csv_file = tmp_path / "test_serial.csv"
    data = [
        ["SN001", "FortiGate 100F"],
        ["SN002", "Cisco ASA 5506"],
        ["SN003", "Palo Alto PA-220"],
    ]

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(data)

    yield csv_file


@pytest.fixture
def sample_csv_with_header(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a sample CSV file with header for testing."""
    csv_file = tmp_path / "test_serial_with_header.csv"
    data = [
        ["serial_number", "product_name"],
        ["SN001", "FortiGate 100F"],
        ["SN002", "Cisco ASA 5506"],
    ]

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(data)

    yield csv_file


@pytest.fixture
def sample_csv_with_duplicates(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a sample CSV file with duplicate serials."""
    csv_file = tmp_path / "test_serial_duplicates.csv"
    data = [
        ["SN001", "FortiGate 100F"],
        ["SN002", "Cisco ASA 5506"],
        ["SN001", "FortiGate 100E"],  # Duplicate serial with different product
    ]

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(data)

    yield csv_file


@pytest.fixture
def output_dir(tmp_path: Path) -> Path:
    """Create a temporary output directory."""
    out_dir = tmp_path / "output"
    out_dir.mkdir(exist_ok=True)
    return out_dir
