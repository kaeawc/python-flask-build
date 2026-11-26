"""Per-request hooks: request IDs, access logging and security headers."""

from __future__ import annotations

import logging
import re
import time
import uuid
from collections.abc import Callable

from flask import Flask, Response, g, request

REQUEST_ID_HEADER = "X-Request-ID"

# Inbound IDs are echoed into logs and responses, so only short, plain tokens are trusted.
_VALID_REQUEST_ID = re.compile(r"[A-Za-z0-9._-]{1,64}")

SECURE_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
    "Cross-Origin-Resource-Policy": "same-origin",
}

access_log = logging.getLogger("python_flask_build.access")


def new_uuid() -> str:
    return uuid.uuid4().hex


def current_request_id() -> str | None:
    request_id: str | None = g.get("request_id")
    return request_id


def install(
    app: Flask,
    new_request_id: Callable[[], str] = new_uuid,
    clock: Callable[[], float] = time.perf_counter,
) -> None:
    """Register the hooks on `app`; `new_request_id` and `clock` are injectable for tests."""

    @app.before_request
    def _start() -> None:
        inbound = request.headers.get(REQUEST_ID_HEADER, "")
        g.request_id = inbound if _VALID_REQUEST_ID.fullmatch(inbound) else new_request_id()
        g.started = clock()

    @app.after_request
    def _finish(response: Response) -> Response:
        request_id = current_request_id()
        if request_id:
            response.headers[REQUEST_ID_HEADER] = request_id
        for name, value in SECURE_HEADERS.items():
            response.headers.setdefault(name, value)
        started = g.get("started")
        duration_ms = round((clock() - started) * 1000, 3) if started is not None else None
        access_log.info(
            "%s %s %s",
            request.method,
            request.path,
            response.status_code,
            extra={"request_id": request_id, "duration_ms": duration_ms},
        )
        return response
