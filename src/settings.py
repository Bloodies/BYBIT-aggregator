"""Module with environment for service."""

import json
from pathlib import Path
from enum import Enum

import inject
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.bybit.bybit import Bybit


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


class BybitSettings(BaseSettings):
    """Postgres connection settings."""

    api_key: str = Field(description="Key for broker")
    api_secret: str = Field(description="")
    endpoints: dict | str = Field(validate_default=True)

    @field_validator("endpoints", mode="before")
    def validate_endpoints(cls, value: str) -> dict:
        with open(APP_DIR / "static" / "bybit_endpoints" / value) as json_file:
            return json.load(json_file)


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
    bybit: BybitSettings


def config(binder: inject.Binder) -> None:
    """Bind application settings.

    Args:
        binder: The inject binder.
    """
    app_settings = ApplicationSettings()  # type: ignore # noqa: PGH003
    binder.bind(ApplicationSettings, app_settings)
    bybit = Bybit(
        api_key=app_settings.bybit.api_key,
        secret_key=app_settings.bybit.api_secret,
        endpoints=app_settings.bybit.endpoints,
    )
    binder.bind(Bybit, bybit)


inject.configure(config)
