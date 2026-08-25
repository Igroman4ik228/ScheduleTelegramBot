from typing import TYPE_CHECKING

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

if TYPE_CHECKING:
    from scheduletelegrambot.database.models import SubscribeModel

PAYMENT_REQUIRED_PRICE = 60


def get_payment_kb(subscribe: SubscribeModel) -> InlineKeyboardMarkup:
    payment_builder = InlineKeyboardBuilder()
    if subscribe.price > PAYMENT_REQUIRED_PRICE:
        payment_builder.add(
            InlineKeyboardButton(
                text="В телеграм",
                callback_data=f"Payment:telegram:{subscribe.id}",
            )
        )

    payment_builder.add(
        InlineKeyboardButton(text="На сайте", callback_data=f"Payment:site:{subscribe.id}")
    )

    return payment_builder.as_markup()
