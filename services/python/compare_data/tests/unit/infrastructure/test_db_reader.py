"""Unit tests for DB reader."""
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from src.domain.exceptions import DatabaseConnectionError
from src.infrastructure.db_reader import DBReader


class TestDBReader:
    """Test cases for DBReader."""

    @patch("src.infrastructure.db_reader.create_engine")
    def test_load_records_success(self, mock_create_engine: MagicMock) -> None:
        """Test successful database record loading."""
        # Setup mock
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn

        # Mock query result
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            ("SN001", "FortiGate 100F"),
            ("SN002", "Cisco ASA 5506"),
        ]
        mock_conn.execute.return_value = mock_result

        # Execute
        reader = DBReader("mysql+pymysql://test:test@localhost/testdb")
        records = reader.load_records()

        # Assert
        assert len(records) == 2
        assert records[0].serial_number == "SN001"
        assert records[0].product_name == "FortiGate 100F"
        assert records[1].serial_number == "SN002"

    @patch("src.infrastructure.db_reader.create_engine")
    def test_load_records_caching(self, mock_create_engine: MagicMock) -> None:
        """Test that records are cached after first load."""
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn

        mock_result = MagicMock()
        mock_result.fetchall.return_value = [("SN001", "Product A")]
        mock_conn.execute.return_value = mock_result

        reader = DBReader("mysql+pymysql://test:test@localhost/testdb")

        records1 = reader.load_records()
        records2 = reader.load_records()

        # Should return same object (cached)
        assert records1 is records2
        # connect should only be called once
        assert mock_engine.connect.call_count == 1

    @patch("src.infrastructure.db_reader.create_engine")
    def test_load_records_empty_serial_skipped(
        self, mock_create_engine: MagicMock
    ) -> None:
        """Test that empty serials are skipped."""
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn

        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            ("SN001", "Product A"),
            ("", "Product B"),  # Empty serial
            (None, "Product C"),  # None serial
            ("SN004", "Product D"),
        ]
        mock_conn.execute.return_value = mock_result

        reader = DBReader("mysql+pymysql://test:test@localhost/testdb")
        records = reader.load_records()

        assert len(records) == 2
        assert records[0].serial_number == "SN001"
        assert records[1].serial_number == "SN004"

    @patch("src.infrastructure.db_reader.create_engine")
    def test_database_connection_error(self, mock_create_engine: MagicMock) -> None:
        """Test error handling for database connection failure."""
        mock_create_engine.side_effect = SQLAlchemyError("Connection refused")

        reader = DBReader("mysql+pymysql://test:test@localhost/testdb")

        with pytest.raises(DatabaseConnectionError) as exc_info:
            reader.load_records()

        assert "Failed to create database engine" in str(exc_info.value)

    @patch("src.infrastructure.db_reader.create_engine")
    def test_database_query_error(self, mock_create_engine: MagicMock) -> None:
        """Test error handling for query execution failure."""
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.side_effect = SQLAlchemyError("Query failed")

        reader = DBReader("mysql+pymysql://test:test@localhost/testdb")

        with pytest.raises(DatabaseConnectionError) as exc_info:
            reader.load_records()

        assert "Database query failed" in str(exc_info.value)

    @patch("src.infrastructure.db_reader.create_engine")
    def test_get_record_count(self, mock_create_engine: MagicMock) -> None:
        """Test record count method."""
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn

        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            ("SN001", "Product A"),
            ("SN002", "Product B"),
        ]
        mock_conn.execute.return_value = mock_result

        reader = DBReader("mysql+pymysql://test:test@localhost/testdb")

        count = reader.get_record_count()

        assert count == 2

    @patch("src.infrastructure.db_reader.create_engine")
    def test_close(self, mock_create_engine: MagicMock) -> None:
        """Test closing database connection."""
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn

        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_conn.execute.return_value = mock_result

        reader = DBReader("mysql+pymysql://test:test@localhost/testdb")
        reader.load_records()
        reader.close()

        mock_engine.dispose.assert_called_once()
        assert reader._engine is None

    @patch("src.infrastructure.db_reader.create_engine")
    def test_trim_whitespace(self, mock_create_engine: MagicMock) -> None:
        """Test that whitespace is trimmed from values."""
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn

        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            ("  SN001  ", "  Product A  "),
        ]
        mock_conn.execute.return_value = mock_result

        reader = DBReader("mysql+pymysql://test:test@localhost/testdb")
        records = reader.load_records()

        assert records[0].serial_number == "SN001"
        assert records[0].product_name == "Product A"
