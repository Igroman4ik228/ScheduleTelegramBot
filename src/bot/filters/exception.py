from typing import cast

from aiogram.filters import Filter
from aiogram.types import TelegramObject
from aiogram.types.error_event import ErrorEvent


class ExceptionTypeFilter(Filter):
    """
    Allows to match exception by type
    """

    __slots__ = ("exceptions",)

    def __init__(self, *exceptions: type[Exception]):
        """
        :param exceptions: Exception type(s)
        """
        if not exceptions:
            raise ValueError("At least one exception type is required")
        self.exceptions = exceptions

    async def __call__(self, obj: TelegramObject) -> bool | dict[str, any]:
        if not isinstance(obj, ErrorEvent):
            return False

        evt = cast(ErrorEvent, obj)
        exc = evt.exception
        if exc is None:
            return False

        if isinstance(exc, self.exceptions):
            return True

        return False
