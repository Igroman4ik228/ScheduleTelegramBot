from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from utils.constants import CallbackData


def get_setting_kb(notify_status: bool,
                   time_display_status: bool):

    notification_text = get_notification_text(notify_status)
    time_text = get_time_text(time_display_status)

    setting_kb = [
        [InlineKeyboardButton(text=notification_text,
                              callback_data=CallbackData.TOGGLE_NOTIFICATION.value)],

        [InlineKeyboardButton(text=time_text,
                              callback_data=CallbackData.TOGGLE_TIME_DISPLAY.value)],
        [InlineKeyboardButton(text="Выбор группы",
                              callback_data=CallbackData.CHOOSE_DEPARTMENT.value)],
    ]

    return InlineKeyboardMarkup(inline_keyboard=setting_kb)


def get_notification_text(notify_status: bool):
    return (
        "🔔 Уведомления включены"
        if notify_status
        else "🔕 Уведомления выключены"
    )


def get_time_text(time_display_status: bool):
    return (
        "⏳ Отображение времени включено"
        if time_display_status
        else "⌛️ Отображение времени выключено"
    )
