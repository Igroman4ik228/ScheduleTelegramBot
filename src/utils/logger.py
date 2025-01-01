from functools import wraps
from logging import Filter, getLogger

from helpers.cls import get_all_methods


# It's useless :(
def with_logger[T](cls: T) -> T:
    """
    Декоратор, добавляющий логгер к классу.

    Args:
        cls: Класс, к которому будет добавлен логгер.
    Returns:
        cls: Класс с добавленным логгером.
    """
    original_init = getattr(cls, '__init__', None)

    @wraps(original_init)
    def new_init(self, *args, **kwargs):
        if hasattr(self, 'logger'):
            self.logger.warning('Logger already set')
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
            if not hasattr(self, 'logger'):
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
    def __init__(self, level=None):
        super().__init__()
        self.level = level

    def filter(self, record):
        if self.level is None:
            return True  # No filtering applied if level is not specified
        return record.levelno == self.level
