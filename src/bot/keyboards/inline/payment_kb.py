from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models.subscribe import SubscribeModel


def get_payment_kb(cost: int) -> InlineKeyboardMarkup:
    payment_builder = InlineKeyboardBuilder()
    payment_builder.add(
        InlineKeyboardButton(text="Yoomoney",
                             callback_data=f"Payment:Yoomoney:{cost}")
    )

    return payment_builder.as_markup()
