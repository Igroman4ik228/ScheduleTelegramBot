import json

from database.db import sessionmaker
from database.models.default_schedule import DefaultScheduleModel
from database.models.groups import GroupModel
from database.repository import Repository


# Асинхронная функция для получения group_id
async def get_group_id(group_name: str):
    async with sessionmaker() as session:
        group: GroupModel = await Repository(session).groups.get_by_name(group_name)
    return group.id


# Основная асинхронная функция
async def process_schedule(file_name: str):
    # Load the JSON data from the file
    with open(f'{file_name}.json', 'r', encoding="UTF-8") as f:
        data = json.load(f)

    # Получаем group_id
    group_id = await get_group_id(file_name)

    # Список для хранения объектов DefaultScheduleModel
    schedule_models = []

    # Проходим по сменам (1 и 2)
    for shift, shift_data in data.items():
        # Проходим по дням недели (0 до 5)
        for weekday, weekday_data in shift_data.items():
            # Создаем объект DefaultScheduleModel
            schedule_model = DefaultScheduleModel(
                weekday=weekday,
                shift=int(shift),
                data_lessons="",
                group_id=group_id
            )

            # Создаем список для уроков
            lessons_list = []

            # Проходим по урокам
            for lesson in weekday_data:
                lessons_list.append(lesson)  # Добавляем урок в список

            # Преобразуем список уроков в JSON и присваиваем его полю data_lessons
            schedule_model.data_lessons = json.dumps(
                lessons_list, ensure_ascii=False)

            # Добавляем объект в список
            schedule_models.append(schedule_model)

    # Печатаем объекты DefaultScheduleModel
    for model in schedule_models:
        print(f"Default Schedule Information:\n"
              f"Weekday: {model.weekday}\n"
              f"Shift: {model.shift}\n"
              f"Data Lessons: {model.data_lessons}\n"
              f"Group ID: {model.group_id}\n")
