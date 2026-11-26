from __future__ import annotations

from collections.abc import Callable

from flask import Flask
from flask.testing import FlaskClient

from python_flask_build.health import app_version


def test_status_keeps_its_original_contract(client: FlaskClient) -> None:
    response = client.get("/status")

    assert response.status_code == 200
    assert response.get_json() == {
        "status": "OK",
        "message": "The application is running smoothly",
        "version": app_version(),
    }


def test_healthz_is_ok_and_not_cached(client: FlaskClient) -> None:
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}
    assert response.headers["Cache-Control"] == "no-store"


def test_readyz_without_checks_is_ready(client: FlaskClient) -> None:
    response = client.get("/readyz")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "checks": {}}
    assert response.headers["Cache-Control"] == "no-store"


def test_readyz_reports_each_check_and_fails_when_one_does(
    make_app: Callable[..., Flask],
) -> None:
    def broken() -> None:
        raise ConnectionError("database unreachable")

    app = make_app(readiness_checks={"cache": lambda: None, "database": broken})

    response = app.test_client().get("/readyz")

    assert response.status_code == 503
    assert response.get_json() == {
        "status": "unavailable",
        "checks": {"cache": "ok", "database": "failed"},
    }


def test_readyz_does_not_leak_check_errors(make_app: Callable[..., Flask]) -> None:
    def broken() -> None:
        raise RuntimeError("password=hunter2")

    response = make_app(readiness_checks={"db": broken}).test_client().get("/readyz")

    assert b"hunter2" not in response.data
