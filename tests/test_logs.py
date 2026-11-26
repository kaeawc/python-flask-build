from __future__ import annotations

import json
import logging
import sys

import pytest

from python_flask_build.logs import JsonFormatter, TextFormatter, _AppHandler, configure_logging


def _record(**extra: object) -> logging.LogRecord:
    record = logging.LogRecord("app", logging.INFO, __file__, 1, "hello %s", ("world",), None)
    record.__dict__.update(extra)
    return record


def test_json_formatter_emits_one_object_with_extra_fields() -> None:
    line = JsonFormatter().format(_record(request_id="r1"))

    entry = json.loads(line)
    assert entry["level"] == "INFO"
    assert entry["logger"] == "app"
    assert entry["message"] == "hello world"
    assert entry["request_id"] == "r1"
    assert "time" in entry


def test_json_formatter_includes_the_exception() -> None:
    try:
        raise ValueError("bad")
    except ValueError:
        record = _record()
        record.exc_info = sys.exc_info()

    entry = json.loads(JsonFormatter().format(record))

    assert "ValueError: bad" in entry["exception"]


def test_text_formatter_appends_extra_fields() -> None:
    assert TextFormatter().format(_record(request_id="r1")).endswith("hello world request_id=r1")
    assert TextFormatter().format(_record()).endswith("hello world")


def test_text_formatter_puts_fields_before_the_traceback() -> None:
    try:
        raise ValueError("bad")
    except ValueError:
        record = _record(request_id="r1")
        record.exc_info = sys.exc_info()

    first_line, *rest = TextFormatter().format(record).splitlines()

    assert first_line.endswith("hello world request_id=r1")
    assert rest[-1] == "ValueError: bad"


def test_configure_logging_replaces_only_its_own_handler(
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = logging.getLogger()
    saved = root.handlers[:], root.level
    foreign = logging.NullHandler()
    root.addHandler(foreign)
    try:
        configure_logging("WARNING", "json")
        configure_logging("WARNING", "json")

        assert len([h for h in root.handlers if isinstance(h, _AppHandler)]) == 1
        assert foreign in root.handlers
        assert root.level == logging.WARNING
        logging.getLogger("t").warning("to stdout")
        assert json.loads(capsys.readouterr().out)["message"] == "to stdout"
    finally:
        root.handlers[:], _ = saved
        root.setLevel(saved[1])
