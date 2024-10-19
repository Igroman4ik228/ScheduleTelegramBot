from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models.subscribe import SubscribeModel


def get_subscribe_kb(subscribes: list[SubscribeModel]) -> InlineKeyboardMarkup:
    subscribe_builder = InlineKeyboardBuilder()
    for subscribe in subscribes:
        subscribe_builder.add(
            InlineKeyboardButton(text=subscribe.name,
                                 callback_data=f"Subscribe:{subscribe.id}")
        )

    return subscribe_builder.as_markup()
