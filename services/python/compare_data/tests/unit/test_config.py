"""Unit tests for config module."""
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from src.config.settings import (
    DatabaseSettings,
    LGUDatabaseSettings,
    Settings,
    get_settings,
)


class TestDatabaseSettings:
    """Test cases for DatabaseSettings."""

    def test_connection_string(self) -> None:
        """Test connection string generation."""
        settings = DatabaseSettings(
            host="localhost",
            port=3306,
            name="testdb",
            user="testuser",
            password="testpass",
        )

        conn_str = settings.get_connection_string()

        assert conn_str == "mysql+pymysql://testuser:testpass@localhost:3306/testdb"

    def test_default_port(self) -> None:
        """Test default port value."""
        settings = DatabaseSettings(
            host="localhost",
            name="testdb",
            user="testuser",
            password="testpass",
        )

        assert settings.port == 3306


class TestLGUDatabaseSettings:
    """Test cases for LGUDatabaseSettings."""

    def test_default_values(self) -> None:
        """Test default values when env vars set explicitly."""
        # When using env_file, pydantic reads from .env
        # So we test with explicit env vars instead
        env_vars = {
            "LGU_DB_HOST": "localhost",
            "LGU_DB_PORT": "3306",
            "LGU_DB_NAME": "mss_uplus",
            "LGU_DB_USER": "root",
            "LGU_DB_PASSWORD": "",
        }
        with patch.dict(os.environ, env_vars, clear=True):
            settings = LGUDatabaseSettings(_env_file=None)

            assert settings.host == "localhost"
            assert settings.port == 3306
            assert settings.name == "mss_uplus"
            assert settings.user == "root"
            assert settings.password == ""

    def test_from_env_vars(self) -> None:
        """Test loading from environment variables."""
        env_vars = {
            "LGU_DB_HOST": "192.168.1.1",
            "LGU_DB_PORT": "3307",
            "LGU_DB_NAME": "custom_db",
            "LGU_DB_USER": "custom_user",
            "LGU_DB_PASSWORD": "custom_pass",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = LGUDatabaseSettings()

            assert settings.host == "192.168.1.1"
            assert settings.port == 3307
            assert settings.name == "custom_db"
            assert settings.user == "custom_user"
            assert settings.password == "custom_pass"


class TestSettings:
    """Test cases for Settings."""

    def test_default_values(self) -> None:
        """Test default values."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()

            assert settings.csv_file_path == Path("lgu_serial.csv")
            assert settings.output_dir == Path("output")
            assert settings.output_format == "xlsx"

    def test_get_lgu_db(self) -> None:
        """Test getting LGU database settings."""
        settings = Settings()
        lgu_db = settings.get_lgu_db()

        assert isinstance(lgu_db, LGUDatabaseSettings)

    def test_ensure_output_dir(self, tmp_path: Path) -> None:
        """Test ensure_output_dir creates directory."""
        new_dir = tmp_path / "new_output"

        with patch.dict(os.environ, {}, clear=True):
            settings = Settings(output_dir=new_dir)

            assert not new_dir.exists()
            result = settings.ensure_output_dir()
            assert new_dir.exists()
            assert result == new_dir


class TestGetSettings:
    """Test cases for get_settings function."""

    def test_caching(self) -> None:
        """Test that settings are cached."""
        # Clear cache first
        get_settings.cache_clear()

        settings1 = get_settings()
        settings2 = get_settings()

        assert settings1 is settings2

    def test_returns_settings_instance(self) -> None:
        """Test that get_settings returns Settings instance."""
        get_settings.cache_clear()
        settings = get_settings()

        assert isinstance(settings, Settings)
