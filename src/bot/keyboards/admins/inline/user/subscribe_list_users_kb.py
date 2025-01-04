from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models import SubscribeModel
from utils.constants import CallbackDataAdmin


class SubscribeCallbackFactory(CallbackData, prefix=CallbackDataAdmin.SUBSCRIBE_LIST_USERS.value):
    subscribe_id: int


def get_subscribe_list_kb(subscribes: list[SubscribeModel]) -> InlineKeyboardMarkup:
    subscribe_builder = InlineKeyboardBuilder()

    for subscribe in subscribes:
        subscribe_builder.add(
            InlineKeyboardButton(
                text=subscribe.name,
                callback_data=SubscribeCallbackFactory(
                    subscribe_id=subscribe.id
                ).pack()
            )
        )

    return subscribe_builder.as_markup()
