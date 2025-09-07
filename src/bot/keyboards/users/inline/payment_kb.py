from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models import SubscribeModel


def get_payment_kb(subscribe: SubscribeModel) -> InlineKeyboardMarkup:
    payment_builder = InlineKeyboardBuilder()
    if subscribe.price > 60:
        payment_builder.add(
            InlineKeyboardButton(
                text="В телеграм",
                callback_data=f"Payment:telegram:{subscribe.id}",
            )
        )

    payment_builder.add(
        InlineKeyboardButton(
            text="На сайте", callback_data=f"Payment:site:{subscribe.id}"
        )
    )

    return payment_builder.as_markup()
