"""Module with environment for service."""

import asyncio
from pathlib import Path
from enum import Enum

from pydantic import AmqpDsn, DirectoryPath, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

APP_DIR = Path(__file__).resolve(strict=True).parent.parent


class LogLevel(str, Enum):
    """Possible log levels."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    FATAL = "FATAL"


class Environment(str, Enum):
    """Where the service was launched."""

    LOCAL = "local"
    DEV = "dev"
    PROD = "prod"


class Settings(BaseSettings):
    """Application settings.

    These parameters can be configured with environment variables.
    """

    environment: Environment = Environment.LOCAL
    log_level: LogLevel = LogLevel.INFO


class ApplicationSettings(BaseSettings):
    """Application settings.

    These parameters can be configured with environment variables.

    Attributes:
        settings: Base settings.
    """

    model_config = SettingsConfigDict(
        env_file=str(APP_DIR / ".env"),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )

    settings: Settings
    api_key: str = Field(default=False, description="Key for broker")
