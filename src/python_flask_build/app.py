"""Application factory. Everything that builds the Flask app goes through `create_app`."""

from __future__ import annotations

from collections.abc import Callable, Mapping

from flask import Flask

from python_flask_build import errors, health, middleware
from python_flask_build.config import Config
from python_flask_build.logs import configure_logging


def create_app(
    config: Config | None = None,
    *,
    readiness_checks: Mapping[str, health.ReadinessCheck] | None = None,
    new_request_id: Callable[[], str] = middleware.new_uuid,
) -> Flask:
    """Build the app. With no `config`, settings come from the environment (see Config.from_env)."""
    config = Config.from_env() if config is None else config
    configure_logging(config.log_level, config.log_format)

    app = Flask(__name__)
    app.config["APP_CONFIG"] = config
    app.json.sort_keys = False  # type: ignore[attr-defined]

    middleware.install(app, new_request_id=new_request_id)
    errors.install(app)
    app.register_blueprint(health.blueprint(readiness_checks or {}))
    return app
