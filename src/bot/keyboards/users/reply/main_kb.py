from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from helpers.user_validate import is_admin


def get_main_kb(user_telegram_id: int):
    main_kb = [
        [KeyboardButton(text="🗓 Расписание")],
        [
            KeyboardButton(text="⬅️ Предыдущее"),
            KeyboardButton(text="Следующее ➡️"),
        ],
        [KeyboardButton(text="👤 Профиль")],
    ]

    # KeyboardButton(text="Техподдержка 🛠")

    if is_admin(user_telegram_id):
        main_kb.append([KeyboardButton(text="🔐 Админ панель")])

    return ReplyKeyboardMarkup(
        keyboard=main_kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите пункт меню",
    )
