import logging
from functools import wraps
from logging import (
    WARNING,
    Filter,
    getLogger,
)
from logging.config import dictConfig
from typing import Any

from helpers.cls import get_all_methods
from utils.constants import ROOT_DIR

LOGS_DIR = ROOT_DIR / "logs"


def logger_configure(config: dict[str, Any]):
    LOGS_DIR.mkdir(exist_ok=True)

    dictConfig(config)

    # Disable sqlalchemy engine logs
    # getLogger("sqlalchemy.engine.Engine").handlers = [NullHandler()]

    # Disable aiogram logs
    for name in [
        # "aiogram.middlewares",
        # "aiogram.event",
        # "aiohttp.access",
        "sqlalchemy.engine.Engine"
    ]:
        getLogger(name).setLevel(WARNING)


# It's useless :(
def with_logger[T](cls: T) -> T:
    """
    Декоратор, добавляющий логгер к классу.

    Args:
        cls: Класс, к которому будет добавлен логгер.
    Returns:
        cls: Класс с добавленным логгером.
    """
    original_init = getattr(cls, "__init__", None)

    @wraps(original_init)
    def new_init(self, *args, **kwargs):
        if hasattr(self, "logger"):
            self.logger.warning("Logger already set")
            if original_init:
                original_init(self, *args, **kwargs)
                return cls

        self.logger = getLogger(self.__class__.__name__)
        if original_init:
            original_init(self, *args, **kwargs)

    cls.__init__ = new_init
    return cls


def log_methods(*methods: str):
    """
    Декоратор, добавляющий логирование вызовов методов класса.

    Args:
        methods: Список имен методов, которые должны быть залогированы.
        Если не передан - логируются все.

    Returns:
        Декорированный класс с логированием указанных методов.
    """

    def decorator[T](cls: T) -> T:
        methods_to_log = set(methods) if methods else get_all_methods(cls)

        # Декорируем методы
        for name in methods_to_log:
            if not hasattr(cls, name):
                continue

            original_method = getattr(cls, name)
            if not callable(original_method):
                continue

            setattr(cls, name, log_decorator(original_method))

        return cls

    def log_decorator(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            if not hasattr(self, "logger"):
                raise RuntimeError(
                    "Logger not set. "
                    "Use self.logger = getLogger(self.__class__.__name__) in __init__ method."
                )

            self.logger.info(f"Method '{method.__name__}' start")
            result = method(self, *args, **kwargs)
            self.logger.info(f"Method '{method.__name__}' end")
            return result

        return wrapper

    return decorator


class LevelFilter(Filter):
    def __init__(self, min_level: int = None, max_level: int = None):
        super().__init__()
        self.min_level = min_level
        self.max_level = max_level

    def filter(self, record):
        if self.min_level is not None and record.levelno < self.min_level:
            return False
        if self.max_level is not None and record.levelno > self.max_level:
            return False
        return True


KB = 1024
MB = KB * 1024

DEFAULT_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(funcName)s:%(lineno)s  -> %(message)s"

LOGGER_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": DEFAULT_FORMAT,
            "datefmt": "%d.%m.%y %H:%M:%S",
        },
        "simple": {
            "format": DEFAULT_FORMAT,
            "datefmt": "%H:%M:%S",
        },
    },
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            "filename": LOGS_DIR / "logs.log",
            "maxBytes": 5 * MB,
            "backupCount": 7,
            "encoding": "utf-8",
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "level": "INFO",
        },
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["file", "console"],
    },
}


LOGGER_CONFIG_EXTRA_FILES = {
    **LOGGER_CONFIG,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "simple",
        },
        "debug_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "default",
            "filename": LOGS_DIR / "debug.log",
            "maxBytes": 1 * MB,
            "backupCount": 1,
            "encoding": "utf8",
            "filters": ["debug_filter"],
        },
        "info_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "default",
            "filename": LOGS_DIR / "info.log",
            "maxBytes": 2 * MB,
            "backupCount": 7,
            "encoding": "utf8",
            "filters": ["info_filter"],
        },
        "warning_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "WARNING",
            "formatter": "default",
            "filename": LOGS_DIR / "warning.log",
            "maxBytes": 3 * MB,
            "backupCount": 7,
            "encoding": "utf8",
            "filters": ["warning_filter"],
        },
        "error_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "default",
            "filename": LOGS_DIR / "error.log",
            "maxBytes": 5 * MB,
            "backupCount": 7,
            "encoding": "utf8",
            "filters": ["error_filter"],
        },
    },
    "filters": {
        "debug_filter": {
            "()": LevelFilter,
            "min_level": logging.DEBUG,
            "max_level": logging.DEBUG,
        },
        "info_filter": {
            "()": LevelFilter,
            "min_level": logging.INFO,
            "max_level": logging.INFO,
        },
        "warning_filter": {
            "()": LevelFilter,
            "min_level": logging.WARNING,
            "max_level": logging.WARNING,
        },
        "error_filter": {
            "()": LevelFilter,
            "min_level": logging.ERROR,
        },
    },
    "root": {
        "level": "DEBUG",
        "handlers": [
            "console",
            "debug_file_handler",
            "info_file_handler",
            "warning_file_handler",
            "error_file_handler",
        ],
    },
}
