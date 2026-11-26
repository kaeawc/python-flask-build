from __future__ import annotations

import itertools
from collections.abc import Callable, Iterator

import pytest
from flask import Flask
from flask.testing import FlaskClient

from python_flask_build import Config, create_app


@pytest.fixture
def make_app() -> Callable[..., Flask]:
    """Build an app with a fixed config and sequential request IDs (req-1, req-2, ...)."""

    def _make(**kwargs: object) -> Flask:
        counter = itertools.count(1)
        kwargs.setdefault("new_request_id", lambda: f"req-{next(counter)}")
        app = create_app(Config(), **kwargs)  # type: ignore[arg-type]
        app.testing = True
        return app

    return _make


@pytest.fixture
def client(make_app: Callable[..., Flask]) -> Iterator[FlaskClient]:
    with make_app().test_client() as c:
        yield c
