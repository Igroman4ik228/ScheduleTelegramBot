from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.db import sessionmaker
from database.repositories.departments import DepartmentRepository


async def get_department_kb() -> InlineKeyboardMarkup:
    async with sessionmaker() as session:
        departments = await DepartmentRepository(session).get_all()

    department_builder = InlineKeyboardBuilder()
    for department in departments:
        department_builder.add(
            InlineKeyboardButton(text=department.name,
                                 callback_data=f"Department:{department.name}")
        )

    return department_builder.as_markup()
