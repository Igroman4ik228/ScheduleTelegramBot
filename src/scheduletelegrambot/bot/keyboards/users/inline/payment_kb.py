
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from scheduletelegrambot.schemas.subscribe import SubscribeBaseSchema

PAYMENT_REQUIRED_PRICE = 60


def get_payment_kb(subscribe: SubscribeBaseSchema) -> InlineKeyboardMarkup:
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
