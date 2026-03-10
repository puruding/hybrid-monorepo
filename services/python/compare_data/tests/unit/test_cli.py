"""Unit tests for CLI module."""
import csv
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.cli.commands import app
from src.domain.models import EquipmentRecord
from typer.testing import CliRunner

runner = CliRunner()


class TestCLI:
    """Test cases for CLI commands."""

    def test_version_command(self) -> None:
        """Test version command."""
        result = runner.invoke(app, ["version"])

        assert result.exit_code == 0
        assert "1.0.0" in result.stdout

    def test_compare_file_not_found(self, tmp_path: Path) -> None:
        """Test compare with non-existent file."""
        result = runner.invoke(
            app, ["compare", "--csv", str(tmp_path / "nonexistent.csv")]
        )

        assert result.exit_code == 1
        assert "not found" in result.stdout

    @patch("src.cli.commands.DBReader")
    @patch("src.cli.commands.get_settings")
    def test_compare_success(
        self,
        mock_get_settings: MagicMock,
        mock_db_reader_class: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test successful comparison."""
        # Create test CSV
        csv_file = tmp_path / "test.csv"
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows([
                ["SN001", "Product A"],
                ["SN002", "Product B"],
            ])

        # Mock settings
        mock_settings = MagicMock()
        mock_settings.csv_file_path = csv_file
        mock_settings.output_dir = tmp_path / "output"
        mock_lgu_db = MagicMock()
        mock_lgu_db.get_connection_string.return_value = "mysql+pymysql://test:test@localhost/test"
        mock_settings.get_lgu_db.return_value = mock_lgu_db
        mock_get_settings.return_value = mock_settings

        # Mock DB reader
        mock_db_reader = MagicMock()
        mock_db_reader.load_records.return_value = [
            EquipmentRecord("SN001", "Product A"),
        ]
        mock_db_reader.get_record_count.return_value = 1
        mock_db_reader_class.return_value = mock_db_reader

        result = runner.invoke(
            app,
            ["compare", "--csv", str(csv_file), "--output", str(tmp_path / "output")],
        )

        assert result.exit_code == 0
        assert "Comparison completed successfully" in result.stdout

    @patch("src.cli.commands.DBReader")
    @patch("src.cli.commands.get_settings")
    def test_compare_with_csv_format(
        self,
        mock_get_settings: MagicMock,
        mock_db_reader_class: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test comparison with CSV output format."""
        # Create test CSV
        csv_file = tmp_path / "test.csv"
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows([["SN001", "Product A"]])

        # Mock settings
        mock_settings = MagicMock()
        mock_settings.csv_file_path = csv_file
        mock_settings.output_dir = tmp_path / "output"
        mock_lgu_db = MagicMock()
        mock_lgu_db.get_connection_string.return_value = "mysql+pymysql://test:test@localhost/test"
        mock_settings.get_lgu_db.return_value = mock_lgu_db
        mock_get_settings.return_value = mock_settings

        # Mock DB reader
        mock_db_reader = MagicMock()
        mock_db_reader.load_records.return_value = []
        mock_db_reader.get_record_count.return_value = 0
        mock_db_reader_class.return_value = mock_db_reader

        result = runner.invoke(
            app,
            [
                "compare",
                "--csv", str(csv_file),
                "--format", "csv",
                "--output", str(tmp_path / "output"),
            ],
        )

        assert result.exit_code == 0

    @patch("src.cli.commands.DBReader")
    @patch("src.cli.commands.get_settings")
    def test_compare_with_header(
        self,
        mock_get_settings: MagicMock,
        mock_db_reader_class: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test comparison with CSV header."""
        # Create test CSV with header
        csv_file = tmp_path / "test.csv"
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows([
                ["serial", "product"],
                ["SN001", "Product A"],
            ])

        # Mock settings
        mock_settings = MagicMock()
        mock_settings.csv_file_path = csv_file
        mock_settings.output_dir = tmp_path / "output"
        mock_lgu_db = MagicMock()
        mock_lgu_db.get_connection_string.return_value = "mysql+pymysql://test:test@localhost/test"
        mock_settings.get_lgu_db.return_value = mock_lgu_db
        mock_get_settings.return_value = mock_settings

        # Mock DB reader
        mock_db_reader = MagicMock()
        mock_db_reader.load_records.return_value = []
        mock_db_reader.get_record_count.return_value = 0
        mock_db_reader_class.return_value = mock_db_reader

        result = runner.invoke(
            app,
            [
                "compare",
                "--csv", str(csv_file),
                "--header",
                "--output", str(tmp_path / "output"),
            ],
        )

        assert result.exit_code == 0

    @patch("src.cli.commands.DBReader")
    @patch("src.cli.commands.get_settings")
    def test_compare_shows_mismatches(
        self,
        mock_get_settings: MagicMock,
        mock_db_reader_class: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test that mismatches are displayed."""
        # Create test CSV
        csv_file = tmp_path / "test.csv"
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows([["SN001", "Product A"]])

        # Mock settings
        mock_settings = MagicMock()
        mock_settings.csv_file_path = csv_file
        mock_settings.output_dir = tmp_path / "output"
        mock_lgu_db = MagicMock()
        mock_lgu_db.get_connection_string.return_value = "mysql+pymysql://test:test@localhost/test"
        mock_settings.get_lgu_db.return_value = mock_lgu_db
        mock_get_settings.return_value = mock_settings

        # Mock DB reader with mismatch
        mock_db_reader = MagicMock()
        mock_db_reader.load_records.return_value = [
            EquipmentRecord("SN001", "Product X"),  # Mismatch
        ]
        mock_db_reader.get_record_count.return_value = 1
        mock_db_reader_class.return_value = mock_db_reader

        result = runner.invoke(
            app,
            [
                "compare",
                "--csv", str(csv_file),
                "--show-mismatches", "5",
                "--output", str(tmp_path / "output"),
            ],
        )

        assert result.exit_code == 0
        assert "Name Mismatch" in result.stdout

    @patch("src.cli.commands.DBReader")
    @patch("src.cli.commands.get_settings")
    def test_compare_with_duplicates(
        self,
        mock_get_settings: MagicMock,
        mock_db_reader_class: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test comparison shows duplicate warnings."""
        # Create test CSV with duplicates
        csv_file = tmp_path / "test.csv"
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows([
                ["SN001", "Product A"],
                ["SN001", "Product B"],  # Duplicate
            ])

        # Mock settings
        mock_settings = MagicMock()
        mock_settings.csv_file_path = csv_file
        mock_settings.output_dir = tmp_path / "output"
        mock_lgu_db = MagicMock()
        mock_lgu_db.get_connection_string.return_value = "mysql+pymysql://test:test@localhost/test"
        mock_settings.get_lgu_db.return_value = mock_lgu_db
        mock_get_settings.return_value = mock_settings

        # Mock DB reader
        mock_db_reader = MagicMock()
        mock_db_reader.load_records.return_value = []
        mock_db_reader.get_record_count.return_value = 0
        mock_db_reader_class.return_value = mock_db_reader

        result = runner.invoke(
            app,
            [
                "compare",
                "--csv", str(csv_file),
                "--output", str(tmp_path / "output"),
            ],
        )

        assert result.exit_code == 0
        assert "Extra Duplicate Source" in result.stdout
