from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models.subscribe import SubscribeModel


def get_subscribe_kb(subscribes: list[SubscribeModel]) -> InlineKeyboardMarkup:
    subscribe_builder = InlineKeyboardBuilder()
    for subscribe in subscribes:
        if subscribe.price <= 0:
            continue

        subscribe_builder.row(
            InlineKeyboardButton(text=f"Подписаться на {subscribe.duration_days} дней за {subscribe.price}₽",
                                 callback_data=f"Subscribe:{subscribe.id}")
        )

    return subscribe_builder.as_markup()
