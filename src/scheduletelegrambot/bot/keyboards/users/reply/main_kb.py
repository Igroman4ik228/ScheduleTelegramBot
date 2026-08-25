from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from scheduletelegrambot.helpers.user_validate import is_admin


def get_main_kb(user_telegram_id: int, admin_ids: list[int]) -> ReplyKeyboardMarkup:
    main_kb = [
        [KeyboardButton(text="🗓 Расписание")],
        [
            KeyboardButton(text="⬅️ Предыдущее"),
            KeyboardButton(text="Следующее ➡️"),
        ],
        [KeyboardButton(text="👤 Профиль")],
    ]

    if is_admin(user_telegram_id, admin_ids):
        main_kb.append([KeyboardButton(text="🔐 Админ панель")])

    return ReplyKeyboardMarkup(
        keyboard=main_kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите пункт меню",
    )
