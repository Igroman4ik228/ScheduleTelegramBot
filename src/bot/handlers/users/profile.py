import asyncio

from aiogram import Bot, F, Router, html
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message

from bot.keyboards.inline.profile_kb import get_profile_kb
from database.models.users import UserModel
from database.redis.profile_cache import ProfileCache
from utils.different import get_info_text

user_locks = {}
router = Router(name=__name__)


@router.message(F.text.lower().contains("профиль"))
async def handle_profile(message: Message, bot: Bot,
                         user: UserModel):
    user_locks.setdefault(message.from_user.id, asyncio.Lock())
    async with user_locks[message.from_user.id]:
        await delete_profile_messages(bot, message.from_user.id, message.chat.id)

        info_text = get_info_text(
            user,
            f"Профиль {html.quote(user.first_name)}"
        )

        sent_message = await message.answer(info_text,
                                            reply_markup=get_profile_kb())

        await ProfileCache().create(message.from_user.id,
                                    sent_message.message_id,
                                    message.message_id)


async def delete_profile_messages(bot: Bot, user_id: int, chat_id: int):
    profile_ids = await ProfileCache().get(user_id)
    if profile_ids is not None:
        setting_message_id, user_settings_message_id = profile_ids
        try:
            await asyncio.gather(bot.delete_message(chat_id, user_settings_message_id),
                                 bot.delete_message(chat_id, setting_message_id))
        except TelegramBadRequest:
            pass
