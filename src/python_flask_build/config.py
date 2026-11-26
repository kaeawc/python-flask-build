"""Settings read from the environment, validated once at startup."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal

LogFormat = Literal["text", "json"]

_LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
_LOG_FORMATS: tuple[LogFormat, ...] = ("text", "json")
_TRUE = ("1", "true", "yes", "on")
_FALSE = ("0", "false", "no", "off", "")


class ConfigError(ValueError):
    """An environment variable is set to a value the app cannot use."""


@dataclass(frozen=True)
class Config:
    host: str = "127.0.0.1"
    port: int = 5000
    debug: bool = False
    log_level: str = "INFO"
    log_format: LogFormat = "text"

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> Config:
        """Build a Config from `env` (default: os.environ); unset variables keep their defaults."""
        env = os.environ if env is None else env
        return cls(
            host=env.get("HOST", cls.host),
            port=_port(env.get("PORT")),
            debug=_bool("DEBUG", env.get("DEBUG")),
            log_level=_choice("LOG_LEVEL", env.get("LOG_LEVEL"), _LOG_LEVELS, cls.log_level),
            log_format=_log_format(env.get("LOG_FORMAT")),
        )


def _port(raw: str | None) -> int:
    if raw is None:
        return Config.port
    try:
        port = int(raw)
    except ValueError:
        raise ConfigError(f"PORT must be an integer, got {raw!r}") from None
    if not 1 <= port <= 65535:
        raise ConfigError(f"PORT must be between 1 and 65535, got {port}")
    return port


def _bool(name: str, raw: str | None) -> bool:
    value = (raw or "").strip().lower()
    if value in _TRUE:
        return True
    if value in _FALSE:
        return False
    raise ConfigError(f"{name} must be a boolean (true/false, 1/0, yes/no, on/off), got {raw!r}")


def _choice(name: str, raw: str | None, allowed: tuple[str, ...], default: str) -> str:
    if raw is None:
        return default
    value = raw.strip().upper()
    if value not in allowed:
        raise ConfigError(f"{name} must be one of {allowed}, got {raw!r}")
    return value


def _log_format(raw: str | None) -> LogFormat:
    if raw is None:
        return Config.log_format
    value = raw.strip().lower()
    for fmt in _LOG_FORMATS:
        if value == fmt:
            return fmt
    raise ConfigError(f"LOG_FORMAT must be one of {_LOG_FORMATS}, got {raw!r}")
