import json
import logging
import logging.config
import os
import sys
from datetime import datetime


class SimpleFormatter(logging.Formatter):
    def __init__(
        self, fmt=None, datefmt=None, style="%", validate=True, *, defaults=None
    ) -> None:
        if fmt is None:
            fmt = "%(asctime)s | %(levelname)s | %(message)s | %(pathname)s:%(lineno)s"
        super(SimpleFormatter, self).__init__(fmt, datefmt, style, validate)


class JSONFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs) -> None:
        super(JSONFormatter, self).__init__(*args, **kwargs)

        self._pid = os.getpid()

    @staticmethod
    def format_timestamp(time: float) -> str:
        return datetime.fromtimestamp(time).isoformat()

    def format(self, record: logging.LogRecord) -> str:
        try:
            msg = record.msg % record.args
        except TypeError:
            msg = record.msg

        extra = {"type": "log"}

        exc = ""
        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
            extra["class"] = str(record.exc_info[0])

        if record.exc_text:
            if exc[-1:] != "\n":
                exc += "\n"
            exc += record.exc_text

        if record.stack_info:
            if exc[-1:] != "\n":
                exc += "\n"
            exc += self.formatStack(record.stack_info)

        if len(exc):
            extra["traceback"] = exc
            extra["type"] = "exception"

        message = {
            "datetime": self.format_timestamp(record.created),
            "level": record.levelname,
            "message": msg,
            "channel": record.name,
            "pid": record.process,
            "context": {
                "processname": record.processName,
                "pathname": record.pathname,
                "module": record.module,
                "function": record.funcName,
                "lineno": record.lineno,
            },
            "extra": extra,
        }

        return json.dumps(message, default=str)


def setup_logging(json: bool = True) -> None:
    LOG_CONFIG = dict(
        version=1,
        disable_existing_loggers=False,
        root={
            "level": "INFO",
            "handlers": ["console"],
        },
        loggers={
            "root": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": True,
            }
        },
        handlers={
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "generic" if json else "simple",
                "stream": sys.stdout,
            },
        },
        formatters={
            "generic": {"class": "remote_log_formatter.JSONFormatter"},
            "simple": {"class": "remote_log_formatter.SimpleFormatter"},
        },
    )

    logging.config.dictConfig(LOG_CONFIG)


def get_logger(name: str = "remote") -> logging.Logger:
    return logging.getLogger(name)
