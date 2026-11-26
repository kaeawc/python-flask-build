"""Every error leaves as the same JSON envelope: {"error": {"code", "message", "requestId"}}."""

from __future__ import annotations

import logging

from flask import Flask, Response, jsonify
from werkzeug.exceptions import HTTPException, InternalServerError

from python_flask_build.middleware import current_request_id

log = logging.getLogger(__name__)


def error_response(status: int, code: str, message: str) -> tuple[Response, int]:
    body = {"error": {"code": code, "message": message, "requestId": current_request_id()}}
    return jsonify(body), status


def install(app: Flask) -> None:
    @app.errorhandler(HTTPException)
    def _http_error(exc: HTTPException) -> Response:
        status = exc.code or 500
        code = (exc.name or "error").lower().replace(" ", "_")
        response, _ = error_response(status, code, exc.description or "")
        response.status_code = status
        # Keep headers the exception carries, such as Allow on a 405.
        for name, value in exc.get_headers():
            if name.lower() != "content-type":
                response.headers[name] = value
        return response

    @app.errorhandler(Exception)
    def _unhandled(exc: Exception) -> tuple[Response, int]:
        # Details go to the log, never to the client.
        log.exception("unhandled error", extra={"request_id": current_request_id()})
        return error_response(500, "internal_server_error", InternalServerError.description)
