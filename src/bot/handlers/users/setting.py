from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.keyboards.inline.setting_kb import (get_notification_text,
                                             get_setting_kb, get_time_text)
from database.models.users import UserModel
from database.redis.repositories import clear_cache
from database.repository import Repository
from utils.constants import CallbackData

router = Router(name=__name__)


@router.callback_query(F.data == CallbackData.SETTING.value)
async def handle_setting(callback_query: CallbackQuery, user: UserModel):
    await callback_query.message.edit_text(f"Настройки, {user}",
                                           reply_markup=get_setting_kb(user.is_notify,
                                                                       user.is_time_shown))


@router.callback_query(F.data == CallbackData.TOGGLE_NOTIFICATION.value)
async def handle_notification(callback_query: CallbackQuery,
                              user: UserModel, repository: Repository):
    user.is_notify = not user.is_notify
    await repository.users.update(user)

    await callback_query.answer(get_notification_text(user.is_notify))
    await callback_query.message.edit_reply_markup(
        reply_markup=get_setting_kb(user.is_notify,
                                    user.is_time_shown)
    )


@router.callback_query(F.data == CallbackData.TOGGLE_TIME_DISPLAY.value)
async def handle_time_display(callback_query: CallbackQuery,
                              user: UserModel, repository: Repository):
    user.is_time_shown = not user.is_time_shown
    await repository.users.update(user)

    await callback_query.answer(get_time_text(user.is_time_shown))
    await callback_query.message.edit_reply_markup(
        reply_markup=get_setting_kb(user.is_notify,
                                    user.is_time_shown)
    )
