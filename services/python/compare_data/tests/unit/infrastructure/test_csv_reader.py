"""Unit tests for CSV reader."""
import csv
from pathlib import Path

import pytest

from src.domain.exceptions import CSVReadError
from src.infrastructure.csv_reader import CSVReader


class TestCSVReader:
    """Test cases for CSVReader."""

    def test_load_records_basic(self, sample_csv_file: Path) -> None:
        """Test basic CSV loading."""
        reader = CSVReader(sample_csv_file, has_header=False)
        records = reader.load_records()

        assert len(records) == 3
        assert records[0].serial_number == "SN001"
        assert records[0].product_name == "FortiGate 100F"

    def test_load_records_with_header(self, sample_csv_with_header: Path) -> None:
        """Test CSV loading with header row."""
        reader = CSVReader(sample_csv_with_header, has_header=True)
        records = reader.load_records()

        assert len(records) == 2
        assert records[0].serial_number == "SN001"

    def test_load_records_with_duplicates(self, sample_csv_with_duplicates: Path) -> None:
        """Test CSV loading with duplicate serials (reader doesn't dedupe)."""
        reader = CSVReader(sample_csv_with_duplicates, has_header=False)
        records = reader.load_records()

        # Reader should return all records, including duplicates
        assert len(records) == 3
        serials = [r.serial_number for r in records]
        assert serials.count("SN001") == 2

    def test_file_not_found(self, tmp_path: Path) -> None:
        """Test error when file not found."""
        reader = CSVReader(tmp_path / "nonexistent.csv")

        with pytest.raises(CSVReadError) as exc_info:
            reader.load_records()

        assert "not found" in str(exc_info.value)

    def test_get_record_count(self, sample_csv_file: Path) -> None:
        """Test record count method."""
        reader = CSVReader(sample_csv_file, has_header=False)

        # Before loading
        count = reader.get_record_count()
        assert count == 3

        # After loading (cached)
        records = reader.load_records()
        count = reader.get_record_count()
        assert count == len(records)

    def test_caching(self, sample_csv_file: Path) -> None:
        """Test that records are cached after first load."""
        reader = CSVReader(sample_csv_file, has_header=False)

        records1 = reader.load_records()
        records2 = reader.load_records()

        # Should return same object (cached)
        assert records1 is records2

    def test_skip_invalid_rows(self, tmp_path: Path) -> None:
        """Test that invalid rows are skipped with warning."""
        csv_file = tmp_path / "invalid.csv"
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["SN001", "Product A"])
            writer.writerow(["SN002"])  # Invalid - only 1 column
            writer.writerow(["SN003", "Product C"])

        reader = CSVReader(csv_file, has_header=False)
        records = reader.load_records()

        # Invalid row should be skipped
        assert len(records) == 2
        assert records[0].serial_number == "SN001"
        assert records[1].serial_number == "SN003"

    def test_skip_empty_serial(self, tmp_path: Path) -> None:
        """Test that rows with empty serial are skipped."""
        csv_file = tmp_path / "empty_serial.csv"
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["SN001", "Product A"])
            writer.writerow(["", "Product B"])  # Empty serial
            writer.writerow(["  ", "Product C"])  # Whitespace serial
            writer.writerow(["SN004", "Product D"])

        reader = CSVReader(csv_file, has_header=False)
        records = reader.load_records()

        # Rows with empty/whitespace serial should be skipped
        assert len(records) == 2
        assert records[0].serial_number == "SN001"
        assert records[1].serial_number == "SN004"

    def test_trim_whitespace(self, tmp_path: Path) -> None:
        """Test that whitespace is trimmed from values."""
        csv_file = tmp_path / "whitespace.csv"
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["  SN001  ", "  Product A  "])

        reader = CSVReader(csv_file, has_header=False)
        records = reader.load_records()

        assert records[0].serial_number == "SN001"
        assert records[0].product_name == "Product A"

    def test_encoding_fallback(self, tmp_path: Path) -> None:
        """Test encoding fallback to cp949."""
        csv_file = tmp_path / "cp949.csv"
        # Write file with cp949 encoding
        with open(csv_file, "w", newline="", encoding="cp949") as f:
            writer = csv.writer(f)
            writer.writerow(["SN001", "한글제품명"])

        # Read with default utf-8 (should fallback to cp949)
        reader = CSVReader(csv_file, encoding="utf-8")
        records = reader.load_records()

        assert len(records) == 1
        assert records[0].product_name == "한글제품명"
