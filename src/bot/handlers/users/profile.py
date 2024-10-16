import asyncio

from aiogram import Bot, F, Router, html
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message

from bot.keyboards.inline.profile_kb import get_profile_kb
from database.models.groups import GroupModel
from database.models.users import UserModel
from database.redis.profile_cache import ProfileCache

user_locks = {}
router = Router(name=__name__)


@router.message(F.text.lower().contains("профиль"))
async def handle_profile(message: Message, bot: Bot,
                         user: UserModel):
    user_locks.setdefault(message.from_user.id, asyncio.Lock())
    async with user_locks[message.from_user.id]:
        await delete_profile_messages(bot, message.from_user.id, message.chat.id)

        answer_text = get_profile_text(user)
        sent_message = await message.answer(answer_text,
                                            reply_markup=get_profile_kb())

        await ProfileCache().create(message.from_user.id,
                                    sent_message.message_id,
                                    message.message_id)


def get_profile_text(user: UserModel) -> str:
    group: GroupModel = user.group
    answer_text = (
        f"Профиль {html.quote(user.first_name)}\n"
        f"Группа: {group.name}\n"
        f"Отображение времени: {user.is_time_shown}\n"
        f"Уведомления: {user.is_notify}"
    )
    return answer_text


async def delete_profile_messages(bot: Bot, user_id: int, chat_id: int):
    profile_ids = await ProfileCache().get(user_id)
    if profile_ids is not None:
        setting_message_id, user_settings_message_id = profile_ids
        try:
            await asyncio.gather(bot.delete_message(chat_id, user_settings_message_id),
                                 bot.delete_message(chat_id, setting_message_id))
        except TelegramBadRequest:
            pass
