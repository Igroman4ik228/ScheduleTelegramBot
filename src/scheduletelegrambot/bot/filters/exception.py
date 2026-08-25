from typing import TYPE_CHECKING, Any, cast

from aiogram.filters import Filter
from aiogram.types.error_event import ErrorEvent

if TYPE_CHECKING:
    from aiogram.types import TelegramObject


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

    async def __call__(self, obj: TelegramObject) -> bool | dict[str, Any]:
        if not isinstance(obj, ErrorEvent):
            return False

        evt = cast("ErrorEvent", obj)
        exc = evt.exception
        if exc is None:
            return False

        return bool(isinstance(exc, self.exceptions))
