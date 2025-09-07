from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models import SubscribeModel
from utils.constants import CallbackData


def get_subscribe_kb(subscribes: list[SubscribeModel]) -> InlineKeyboardMarkup:
    subscribe_builder = InlineKeyboardBuilder()

    subscribe_builder.row(
        InlineKeyboardButton(
            text="Реферальная система",
            callback_data=CallbackData.REFERRAL.value,
        )
    )

    for subscribe in subscribes:
        if subscribe.price <= 0:
            continue

        subscribe_builder.row(
            InlineKeyboardButton(
                text=f"Подписаться на {subscribe.duration_days} "
                f"дней за {subscribe.price}₽",
                callback_data=f"Subscribe:{subscribe.id}",
            )
        )

    return subscribe_builder.as_markup()
