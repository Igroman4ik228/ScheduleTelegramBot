from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from bot.filters.subscribe import SubscribeFilter
from utils.constants import CallbackData

router = Router(name=__name__)


@router.message(~SubscribeFilter())
async def handle_check_subscribe(message: Message):
    await message.answer("Купите пожалуйста подписку!")


@router.callback_query(~SubscribeFilter())
async def handle_check_subscribe_callback(callback_query: CallbackQuery):
    await callback_query.message.answer("Купите пожалуйста подписку!")
