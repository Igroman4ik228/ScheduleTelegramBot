from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from scheduletelegrambot.bot.keyboards.users.inline.callbacks import GroupCallback
from scheduletelegrambot.schemas.group import GroupBaseSchema


def get_group_kb(groups: list[GroupBaseSchema]) -> InlineKeyboardMarkup:
    group_builder = InlineKeyboardBuilder()
    for group in groups:
        group_builder.add(
            InlineKeyboardButton(text=group.name, callback_data=GroupCallback(id=group.id).pack())
        )

    return group_builder.as_markup()
