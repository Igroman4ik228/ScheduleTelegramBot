from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from bot.filters.subscribe import SubscribeFilter
from bot.keyboards.inline.payment_kb import get_payment_kb
from bot.keyboards.inline.subscribe_kb import get_subscribe_kb
from database.models.subscribe import SubscribeModel
from database.repository import Repository
from utils.constants import CallbackData

router = Router(name=__name__)

# @router.message(~SubscribeFilter())
# async def handle_check_subscribe(message: Message, repository: Repository):
#     subscribes = await repository.subscribes.get_all()
#     description = get_subscribes_description(subscribes)
#     await message.answer("Купите пожалуйста подписку!\n"
#                          f"{description}",
#                          reply_markup=get_subscribe_kb(subscribes))


# @router.callback_query(~SubscribeFilter())
# async def handle_check_subscribe_callback(callback_query: CallbackQuery, repository: Repository):
#     subscribes = await repository.subscribes.get_all()
#     description = get_subscribes_description(subscribes)
#     await callback_query.message.answer("Купите пожалуйста подписку!\n"
#                                         f"{description}",
#                                         reply_markup=get_subscribe_kb(subscribes))


@router.callback_query(F.data == CallbackData.SUBSCRIBE.value)
async def handle_subscribe(callback_query: CallbackQuery, repository: Repository):
    subscribes = await repository.subscribes.get_all()
    description = get_subscribes_description(subscribes)
    await callback_query.message.edit_text(description,
                                           reply_markup=get_subscribe_kb(subscribes))


def get_subscribes_description(subscribes: list[SubscribeModel]):
    description = ""
    for subscribe in subscribes:
        description += f"{subscribe.name}\n"
        if subscribe.description is not None:
            description += f"{subscribe.description}\n"
        description += "\n"

    return description


@router.callback_query(F.data.startswith("Subscribe:"))
async def handle_choose_subscribe(callback_query: CallbackQuery, repository: Repository):
    subscribe_id = callback_query.data.split(":")[1]
    subscribe = await repository.subscribes.get(subscribe_id)
    await callback_query.message.answer(f"Вы выбрали: {subscribe.name}\n"
                                        f"Стоимость: {subscribe.cost}\n"
                                        "Выберите способ оплаты:",
                                        reply_markup=get_payment_kb(subscribe.cost))


@router.callback_query(F.data.startswith("Payment:Yoomoney:"))
async def handle_payment(callback_query: CallbackQuery):
    cost = callback_query.data.split(":")[2]
    await callback_query.message.answer(f"Оплата через ЮMoney: {cost}...")


def update_subscribe():
    pass
