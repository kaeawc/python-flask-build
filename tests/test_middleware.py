from __future__ import annotations

from collections.abc import Callable, Iterator

import pytest
from flask import Flask
from flask.testing import FlaskClient

from python_flask_build import middleware
from python_flask_build.middleware import REQUEST_ID_HEADER, SECURE_HEADERS


def test_generates_a_request_id_per_request(client: FlaskClient) -> None:
    assert client.get("/healthz").headers[REQUEST_ID_HEADER] == "req-1"
    assert client.get("/healthz").headers[REQUEST_ID_HEADER] == "req-2"


def test_echoes_a_valid_inbound_request_id(client: FlaskClient) -> None:
    response = client.get("/healthz", headers={REQUEST_ID_HEADER: "abc-123.DEF_4"})

    assert response.headers[REQUEST_ID_HEADER] == "abc-123.DEF_4"


@pytest.mark.parametrize("bad", ["", "a" * 65, "has space", "inject\r\nX-Evil: 1", "<script>"])
def test_replaces_an_unsafe_inbound_request_id(client: FlaskClient, bad: str) -> None:
    response = client.get("/healthz", environ_overrides={"HTTP_X_REQUEST_ID": bad})

    assert response.headers[REQUEST_ID_HEADER] == "req-1"


def test_sets_security_headers_on_every_response(client: FlaskClient) -> None:
    for path in ("/healthz", "/missing"):
        response = client.get(path)
        for name, value in SECURE_HEADERS.items():
            assert response.headers[name] == value


def test_default_request_ids_are_unique_hex() -> None:
    ids = {middleware.new_uuid() for _ in range(100)}

    assert len(ids) == 100
    assert all(len(i) == 32 and int(i, 16) >= 0 for i in ids)


def test_access_log_records_method_path_status_and_duration(
    caplog: pytest.LogCaptureFixture,
) -> None:
    ticks: Iterator[float] = iter([10.0, 10.25])
    app = Flask(__name__)
    middleware.install(app, new_request_id=lambda: "fixed", clock=lambda: next(ticks))
    app.add_url_rule("/x", "x", lambda: "ok")

    with caplog.at_level("INFO", logger="python_flask_build.access"):
        app.test_client().get("/x")

    (record,) = [r for r in caplog.records if r.name == "python_flask_build.access"]
    assert record.getMessage() == "GET /x 200"
    assert record.__dict__["request_id"] == "fixed"
    assert record.__dict__["duration_ms"] == 250.0


def test_hooks_tolerate_a_request_that_skipped_before_request(
    make_app: Callable[..., Flask],
) -> None:
    app = make_app()
    # A before_request hook registered first that short-circuits leaves no request ID or timer.
    app.before_request_funcs.setdefault(None, []).insert(0, lambda: ("short", 200))

    response = app.test_client().get("/healthz")

    assert response.get_data(as_text=True) == "short"
    assert REQUEST_ID_HEADER not in response.headers
