from __future__ import annotations

from collections.abc import Callable

import pytest
from flask import Flask
from flask.testing import FlaskClient


def test_unknown_route_returns_json_404(client: FlaskClient) -> None:
    response = client.get("/nope")

    assert response.status_code == 404
    assert response.is_json
    assert response.get_json()["error"]["code"] == "not_found"
    assert response.get_json()["error"]["requestId"] == "req-1"


def test_wrong_method_returns_405_with_allow_header(client: FlaskClient) -> None:
    response = client.post("/status")

    assert response.status_code == 405
    assert response.is_json
    assert response.get_json()["error"]["code"] == "method_not_allowed"
    assert "GET" in response.headers["Allow"]


def test_unhandled_exception_returns_generic_500_and_logs_it(
    make_app: Callable[..., Flask], caplog: pytest.LogCaptureFixture
) -> None:
    app = make_app()

    @app.get("/boom")
    def boom() -> str:
        raise RuntimeError("secret detail")

    response = app.test_client().get("/boom")

    assert response.status_code == 500
    body = response.get_json()
    assert body["error"]["code"] == "internal_server_error"
    assert "secret detail" not in response.get_data(as_text=True)
    assert any(r.exc_info and "secret detail" in str(r.exc_info[1]) for r in caplog.records)
