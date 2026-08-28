from aiogram.filters.callback_data import CallbackData


class DepartmentCallback(CallbackData, prefix="dept"):
    id: int


class GroupCallback(CallbackData, prefix="group"):
    id: int
