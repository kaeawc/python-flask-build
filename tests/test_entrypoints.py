from __future__ import annotations

import runpy
from pathlib import Path
from typing import Any

import pytest
from flask import Flask

from python_flask_build import __main__ as dev_server

ROOT = Path(__file__).resolve().parent.parent


def test_dev_server_runs_with_settings_from_the_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[dict[str, Any]] = []
    monkeypatch.setattr(Flask, "run", lambda self, **kw: calls.append(kw))
    monkeypatch.setenv("PORT", "5050")
    monkeypatch.setenv("DEBUG", "false")

    dev_server.main()

    assert calls == [{"host": "127.0.0.1", "port": 5050, "debug": False}]


def test_wsgi_module_exposes_an_app() -> None:
    from python_flask_build.wsgi import app

    assert isinstance(app, Flask)


def test_gunicorn_config_binds_port_from_the_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PORT", "8000")
    monkeypatch.setenv("WEB_CONCURRENCY", "3")
    monkeypatch.setenv("LOG_LEVEL", "WARNING")

    settings = runpy.run_path(str(ROOT / "gunicorn.conf.py"))

    assert settings["bind"] == "0.0.0.0:8000"
    assert settings["workers"] == 3
    assert settings["loglevel"] == "warning"
    assert settings["wsgi_app"] == "python_flask_build.wsgi:app"
    assert settings["control_socket_disable"] is True
