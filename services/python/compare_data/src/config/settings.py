"""Pydantic Settings for configuration management."""
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database connection settings."""

    host: str
    port: int = 3306
    name: str
    user: str
    password: str

    def get_connection_string(self) -> str:
        """Generate SQLAlchemy connection string."""
        return (
            f"mysql+pymysql://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}"
        )


class LGUDatabaseSettings(DatabaseSettings):
    """LGU Database settings with LGU_ prefix."""

    model_config = SettingsConfigDict(
        env_prefix="LGU_DB_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: str = Field(default="localhost")
    port: int = Field(default=3306)
    name: str = Field(default="mss_uplus")
    user: str = Field(default="root")
    password: str = Field(default="")


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # CSV file path
    csv_file_path: Path = Field(
        default=Path("lgu_serial.csv"),
        description="Path to the source CSV file",
    )

    # Output settings
    output_dir: Path = Field(
        default=Path("output"),
        description="Directory for output reports",
    )
    output_format: Literal["xlsx", "csv", "both"] = Field(
        default="xlsx",
        description="Output format for reports",
    )

    def get_lgu_db(self) -> LGUDatabaseSettings:
        """Get LGU database settings."""
        return LGUDatabaseSettings()

    def ensure_output_dir(self) -> Path:
        """Ensure output directory exists and return it."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        return self.output_dir


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
