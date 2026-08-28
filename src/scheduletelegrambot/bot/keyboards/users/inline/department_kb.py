from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from scheduletelegrambot.bot.keyboards.users.inline.callbacks import DepartmentCallback
from scheduletelegrambot.schemas.department import DepartmentBaseSchema


def get_department_kb(
    departments: list[DepartmentBaseSchema],
) -> InlineKeyboardMarkup:
    department_builder = InlineKeyboardBuilder()
    for department in departments:
        department_builder.add(
            InlineKeyboardButton(
                text=department.name,
                callback_data=DepartmentCallback(id=department.id).pack(),
            )
        )

    return department_builder.as_markup()
