from __future__ import annotations

import pytest

from python_flask_build import Config, ConfigError


def test_defaults_when_nothing_is_set() -> None:
    assert Config.from_env({}) == Config()


def test_reads_every_variable() -> None:
    env = {
        "HOST": "0.0.0.0",
        "PORT": "8080",
        "DEBUG": "true",
        "LOG_LEVEL": "debug",
        "LOG_FORMAT": "JSON",
    }

    assert Config.from_env(env) == Config(
        host="0.0.0.0", port=8080, debug=True, log_level="DEBUG", log_format="json"
    )


def test_reads_os_environ_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PORT", "6000")

    assert Config.from_env().port == 6000


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("1", True), ("YES", True), ("on", True), ("0", False), ("off", False), ("", False)],
)
def test_debug_accepts_common_boolean_spellings(raw: str, expected: bool) -> None:
    assert Config.from_env({"DEBUG": raw}).debug is expected


@pytest.mark.parametrize(
    ("env", "message"),
    [
        ({"PORT": "http"}, "PORT must be an integer"),
        ({"PORT": "0"}, "PORT must be between 1 and 65535"),
        ({"PORT": "65536"}, "PORT must be between 1 and 65535"),
        ({"DEBUG": "maybe"}, "DEBUG must be a boolean"),
        ({"LOG_LEVEL": "verbose"}, "LOG_LEVEL must be one of"),
        ({"LOG_FORMAT": "xml"}, "LOG_FORMAT must be one of"),
    ],
)
def test_rejects_invalid_values_naming_the_variable(env: dict[str, str], message: str) -> None:
    with pytest.raises(ConfigError, match=message):
        Config.from_env(env)
