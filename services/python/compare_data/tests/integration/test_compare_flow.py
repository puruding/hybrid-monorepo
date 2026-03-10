"""Integration tests for the full comparison flow."""
import csv
from pathlib import Path

import pytest

from src.application.compare_usecase import CompareUseCase
from src.domain.models import EquipmentRecord
from src.infrastructure.csv_reader import CSVReader
from src.infrastructure.report_writer import ReportWriter


class MockDBReader:
    """Mock database reader for testing."""

    def __init__(self, records: list[EquipmentRecord]) -> None:
        self._records = records

    def load_records(self) -> list[EquipmentRecord]:
        return self._records

    def get_record_count(self) -> int:
        return len(self._records)


@pytest.fixture
def integration_csv_file(tmp_path: Path) -> Path:
    """Create integration test CSV file."""
    csv_file = tmp_path / "source.csv"
    data = [
        ["SN001", "FortiGate 100F"],
        ["SN002", "Cisco ASA 5506"],
        ["SN003", "Palo Alto PA-220"],
        ["SN004", "FortiGate 100F"],  # Same product as SN001
        ["SN005", "Juniper SRX300"],
    ]

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(data)

    return csv_file


@pytest.fixture
def integration_db_records() -> list[EquipmentRecord]:
    """Create integration test DB records."""
    return [
        EquipmentRecord("SN001", "FortiGate 100F"),  # Match
        EquipmentRecord("SN002", "Cisco ASA 5505"),  # Name mismatch
        EquipmentRecord("SN003", "Palo Alto PA-220"),  # Match
        EquipmentRecord("SN006", "Check Point 1100"),  # Target only
    ]


class TestCompareFlow:
    """Integration tests for full comparison flow."""

    def test_full_comparison_flow(
        self,
        integration_csv_file: Path,
        integration_db_records: list[EquipmentRecord],
        tmp_path: Path,
    ) -> None:
        """Test complete comparison flow."""
        # Setup
        source_reader = CSVReader(integration_csv_file, has_header=False)
        target_reader = MockDBReader(integration_db_records)
        output_dir = tmp_path / "output"
        report_writer = ReportWriter(output_dir)

        # Execute
        usecase = CompareUseCase(
            source_port=source_reader,
            target_port=target_reader,
            report_writer=report_writer,
            output_format="xlsx",
        )
        result = usecase.execute()

        # Assert summary
        assert result.summary.total_source == 5
        assert result.summary.total_target == 4
        assert result.summary.matched_count == 2  # SN001, SN003
        assert result.summary.name_mismatch_count == 1  # SN002
        assert result.summary.source_only_count == 2  # SN004, SN005
        assert result.summary.target_only_count == 1  # SN006

        # Assert product counts
        assert len(result.product_counts) > 0
        fortigate_count = next(
            (p for p in result.product_counts if p.product_name == "FortiGate 100F"),
            None,
        )
        assert fortigate_count is not None
        assert fortigate_count.source_count == 2  # SN001, SN004
        assert fortigate_count.target_count == 1  # SN001

        # Assert report generated
        assert len(result.report_paths) == 1
        assert result.report_paths[0].exists()
        assert result.report_paths[0].suffix == ".xlsx"

        # Assert mathematical consistency
        assert result.summary.validate_consistency()

    def test_comparison_with_duplicates(
        self,
        tmp_path: Path,
    ) -> None:
        """Test comparison with duplicate serials."""
        # Create CSV with duplicates
        csv_file = tmp_path / "source_dup.csv"
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows([
                ["SN001", "Product A"],
                ["SN001", "Product B"],  # Duplicate
                ["SN002", "Product C"],
            ])

        # DB records
        db_records = [
            EquipmentRecord("SN001", "Product A"),
        ]

        source_reader = CSVReader(csv_file, has_header=False)
        target_reader = MockDBReader(db_records)
        output_dir = tmp_path / "output"
        report_writer = ReportWriter(output_dir)

        usecase = CompareUseCase(
            source_port=source_reader,
            target_port=target_reader,
            report_writer=report_writer,
            output_format="xlsx",
        )
        result = usecase.execute()

        # Assert duplicates detected
        assert result.summary.extra_duplicate_source_count == 1
        assert len(result.duplicates) == 1
        assert result.duplicates[0].serial_number == "SN001"
        assert result.duplicates[0].occurrence_count == 2

        # Assert first record used for comparison
        assert result.summary.matched_count == 1  # SN001 Product A matches

    def test_comparison_csv_output(
        self,
        integration_csv_file: Path,
        integration_db_records: list[EquipmentRecord],
        tmp_path: Path,
    ) -> None:
        """Test comparison with CSV output format."""
        source_reader = CSVReader(integration_csv_file, has_header=False)
        target_reader = MockDBReader(integration_db_records)
        output_dir = tmp_path / "output"
        report_writer = ReportWriter(output_dir)

        usecase = CompareUseCase(
            source_port=source_reader,
            target_port=target_reader,
            report_writer=report_writer,
            output_format="csv",
        )
        result = usecase.execute()

        # Should generate multiple CSV files
        assert len(result.report_paths) == 4
        for path in result.report_paths:
            assert path.exists()
            assert path.suffix == ".csv"

    def test_comparison_both_output(
        self,
        integration_csv_file: Path,
        integration_db_records: list[EquipmentRecord],
        tmp_path: Path,
    ) -> None:
        """Test comparison with both output formats."""
        source_reader = CSVReader(integration_csv_file, has_header=False)
        target_reader = MockDBReader(integration_db_records)
        output_dir = tmp_path / "output"
        report_writer = ReportWriter(output_dir)

        usecase = CompareUseCase(
            source_port=source_reader,
            target_port=target_reader,
            report_writer=report_writer,
            output_format="both",
        )
        result = usecase.execute()

        # Should generate 1 Excel + 4 CSV files
        assert len(result.report_paths) == 5
        xlsx_count = sum(1 for p in result.report_paths if p.suffix == ".xlsx")
        csv_count = sum(1 for p in result.report_paths if p.suffix == ".csv")
        assert xlsx_count == 1
        assert csv_count == 4

    def test_empty_source(
        self,
        integration_db_records: list[EquipmentRecord],
        tmp_path: Path,
    ) -> None:
        """Test comparison with empty source."""
        # Empty CSV
        csv_file = tmp_path / "empty.csv"
        csv_file.touch()

        source_reader = CSVReader(csv_file, has_header=False)
        target_reader = MockDBReader(integration_db_records)
        output_dir = tmp_path / "output"
        report_writer = ReportWriter(output_dir)

        usecase = CompareUseCase(
            source_port=source_reader,
            target_port=target_reader,
            report_writer=report_writer,
            output_format="xlsx",
        )
        result = usecase.execute()

        assert result.summary.total_source == 0
        assert result.summary.total_target == 4
        assert result.summary.target_only_count == 4
        assert result.summary.matched_count == 0

    def test_empty_target(
        self,
        integration_csv_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test comparison with empty target."""
        source_reader = CSVReader(integration_csv_file, has_header=False)
        target_reader = MockDBReader([])
        output_dir = tmp_path / "output"
        report_writer = ReportWriter(output_dir)

        usecase = CompareUseCase(
            source_port=source_reader,
            target_port=target_reader,
            report_writer=report_writer,
            output_format="xlsx",
        )
        result = usecase.execute()

        assert result.summary.total_source == 5
        assert result.summary.total_target == 0
        assert result.summary.source_only_count == 5
        assert result.summary.matched_count == 0
