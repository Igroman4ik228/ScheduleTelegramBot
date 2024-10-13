from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models.groups import GroupModel


async def get_group_kb(groups: list[GroupModel]) -> InlineKeyboardMarkup:
    group_builder = InlineKeyboardBuilder()
    for group in groups:
        group_builder.add(
            InlineKeyboardButton(text=group.name,
                                 callback_data=f"Group:{group.name}")
        )

    return group_builder.as_markup()
