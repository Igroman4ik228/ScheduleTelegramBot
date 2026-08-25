from typing import TYPE_CHECKING

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

if TYPE_CHECKING:
    from scheduletelegrambot.database.models import DepartmentModel


def get_department_kb(
    departments: list[DepartmentModel],
) -> InlineKeyboardMarkup:
    department_builder = InlineKeyboardBuilder()
    for department in departments:
        department_builder.add(
            InlineKeyboardButton(
                text=department.name,
                callback_data=f"Department:{department.name}",
            )
        )

    return department_builder.as_markup()
