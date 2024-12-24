import asyncio

from aiogram import Bot, F, Router, html
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message

from bot.keyboards.users.inline.profile_kb import get_profile_kb
from database.models.groups import GroupModel
from database.models.subscribe import SubscribeModel
from database.models.users import UserModel
from database.redis.profile_cache import ProfileCache
from database.repository import Repository
from services.formatter_service.message import ProfileFormatter

user_locks = {}
router = Router(name=__name__)


@router.message(F.text.lower().contains("профиль"))
async def handle_profile(message: Message, bot: Bot,
                         user: UserModel, repository: Repository):
    group: GroupModel = user.group
    department = await repository.departments.get(group.department_id)
    subscribe: SubscribeModel = user.subscribe

    user_locks.setdefault(message.from_user.id, asyncio.Lock())
    async with user_locks[message.from_user.id]:
        await delete_profile_messages(bot, message.from_user.id, message.chat.id)

        info_text = ProfileFormatter(
            user, group, department, subscribe
        ).format_info(f"Профиль {user.user_name}")

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
