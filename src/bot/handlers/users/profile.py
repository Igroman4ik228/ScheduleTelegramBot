import asyncio

from aiogram import Bot, F, Router, html
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message

from bot.keyboards.users.inline.profile_kb import get_profile_kb
from bot.views.profile import ProfileView
from database.models import GroupModel, SubscribeModel, UserModel
from database.redis.profile_cache import ProfileCache
from database.repository import Repository

user_locks = {}
router = Router(name=__name__)

TITLE = "Профиль @{user_name}"


@router.message(F.text.lower().contains("профиль"))
async def handle_profile(
    message: Message, bot: Bot, user: UserModel, repository: Repository
):
    title = html.blockquote(TITLE.format(user_name=user.user_name))

    group: GroupModel = user.group
    department = await repository.departments.get(group.department_id)
    subscribe: SubscribeModel = user.subscribe
    info_text = ProfileView.format_info(
        department.name, group.name, subscribe.name, user.subscribe_end_time
    )

    user_locks.setdefault(message.from_user.id, asyncio.Lock())
    async with user_locks[message.from_user.id]:
        await delete_profile_messages(
            bot, message.from_user.id, message.chat.id
        )

        sent_message = await message.answer(
            title + info_text, reply_markup=get_profile_kb()
        )

        await ProfileCache().create(
            message.from_user.id, sent_message.message_id, message.message_id
        )


async def delete_profile_messages(bot: Bot, user_id: int, chat_id: int):
    profile_ids = await ProfileCache().get(user_id)
    if profile_ids is not None:
        setting_message_id, user_settings_message_id = profile_ids
        try:
            await asyncio.gather(
                bot.delete_message(chat_id, user_settings_message_id),
                bot.delete_message(chat_id, setting_message_id),
            )
        except TelegramBadRequest:
            pass
