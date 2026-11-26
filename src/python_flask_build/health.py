"""Liveness and readiness probes, plus the legacy /status endpoint."""

from __future__ import annotations

import logging
from collections.abc import Callable, Mapping
from importlib.metadata import PackageNotFoundError, version

from flask import Blueprint, Response, jsonify

# A readiness check returns normally when its dependency is usable and raises when it is not.
ReadinessCheck = Callable[[], None]

log = logging.getLogger(__name__)


def app_version() -> str:
    try:
        return version("python-flask-build")
    except PackageNotFoundError:  # pragma: no cover - only when running from an uninstalled tree
        return "unknown"


def blueprint(checks: Mapping[str, ReadinessCheck]) -> Blueprint:
    bp = Blueprint("health", __name__)

    @bp.get("/status")
    def status() -> Response:
        return jsonify(
            status="OK",
            message="The application is running smoothly",
            version=app_version(),
        )

    @bp.get("/healthz")
    def healthz() -> Response:
        """Liveness: the process can serve requests. Never touches dependencies."""
        return _no_store(jsonify(status="ok"))

    @bp.get("/readyz")
    def readyz() -> Response:
        """Readiness: every registered dependency check passes."""
        results: dict[str, str] = {}
        for name, check in checks.items():
            try:
                check()
                results[name] = "ok"
            except Exception:
                log.warning("readiness check %s failed", name, exc_info=True)
                results[name] = "failed"
        ready = all(r == "ok" for r in results.values())
        response = jsonify(status="ok" if ready else "unavailable", checks=results)
        response.status_code = 200 if ready else 503
        return _no_store(response)

    return bp


def _no_store(response: Response) -> Response:
    response.headers["Cache-Control"] = "no-store"
    return response
