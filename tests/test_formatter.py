import json
import logging
from dataclasses import dataclass
from decimal import Decimal
from functools import lru_cache
from typing import Any

import pytest

from remote_log_formatter import JSONFormatter, SimpleFormatter
from remote_log_formatter import get_logger as _logger
from remote_log_formatter import setup_logging as _setup


@lru_cache()
@pytest.fixture()
def logger_json() -> None:
    _setup()
    return _logger()


@lru_cache()
@pytest.fixture()
def logger_plain() -> None:
    _setup(json=False)
    return _logger()


@dataclass(frozen=True)
class Foo:
    bar: str


@lru_cache()
@pytest.mark.parametrize(
    "message,expected",
    [
        pytest.param("foo", "foo", id="str"),
        pytest.param(42, 42, id="integer"),
        pytest.param(Decimal(42), "42", id="decimal"),
        pytest.param(42.0, 42.0, id="float"),
        pytest.param(Foo(bar=42), "Foo(bar=42)", id="dataclass"),
    ],
)
def test_json_logger(
    logger_json: logging.Logger,
    caplog: pytest.LogCaptureFixture,
    message: Any,
    expected: str,
) -> None:
    logger_json.info(message)
    assert caplog.records
    r = caplog.records[0]

    data = json.loads(JSONFormatter().format(r))
    assert data == {
        "datetime": data["datetime"],
        "level": "INFO",
        "message": expected,
        "channel": "remote",
        "pid": data["pid"],
        "context": {
            "processname": "MainProcess",
            "pathname": data["context"]["pathname"],
            "module": "test_formatter",
            "function": "test_json_logger",
            "lineno": data["context"]["lineno"],
        },
        "extra": {"type": "log"},
    }


@lru_cache()
@pytest.mark.parametrize(
    "message,expected",
    [
        pytest.param("foo", "foo", id="str"),
        pytest.param(42, "42", id="integer"),
        pytest.param(Decimal(42), "42", id="decimal"),
        pytest.param(42.0, "42.0", id="float"),
        pytest.param(Foo(bar=42), "Foo(bar=42)", id="dataclass"),
    ],
)
def test_plain_logger(
    logger_plain: logging.Logger,
    caplog: pytest.LogCaptureFixture,
    message: Any,
    expected: str,
) -> None:
    logger_plain.info(message)
    assert caplog.records
    r = caplog.records[0]
    data = SimpleFormatter().format(r)

    _ts, level, message, path = data.split("|")
    assert message.strip() == expected
    assert level.strip() == "INFO"
