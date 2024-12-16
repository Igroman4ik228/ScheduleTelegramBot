from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models.groups import GroupModel
from utils.constants import CallbackDataAdmin


class GroupCallbackFactory(CallbackData, prefix=CallbackDataAdmin.GROUP_LIST_USERS.value):
    group_id: int
    group_name: str


def get_group_kb(groups: list[GroupModel]) -> InlineKeyboardMarkup:
    group_builder = InlineKeyboardBuilder()
    for group in groups:
        group_builder.add(
            InlineKeyboardButton(text=group.name,
                                 callback_data=GroupCallbackFactory(
                                     group_id=group.id,
                                     group_name=group.name
                                 ).pack())
        )

    return group_builder.as_markup()
