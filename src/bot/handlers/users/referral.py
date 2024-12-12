from aiogram import Bot, F, Router, html
from aiogram.types import CallbackQuery

from database.repository import Repository
from utils.constants import MAX_REFERRAL, CallbackData

router = Router(name=__name__)

TITLE = "Приветствие"


@router.callback_query(F.data == CallbackData.REFERRAL.value)
async def handle_referral(callback_query: CallbackQuery, bot: Bot, repository: Repository):
    tg_id = callback_query.from_user.id
    bot_name = await bot.get_my_name()

    referral_url = f"https://t.me/{bot_name.name}?start={tg_id}"
    referral_url = html.code(referral_url)
    result_text = f"{referral_url}\n"

    user = await repository.users.get(tg_id)
    result_text += "Количество пользователей зарегистрированных по вашей ссылке: "
    result_text += f"{user.count_referral}/{MAX_REFERRAL}"

    await callback_query.answer()
    await callback_query.message.answer(result_text)
