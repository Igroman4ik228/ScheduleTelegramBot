from ast import literal_eval

from aiogram import F, Router
from aiogram.types import Message

from bot.keyboards.reply.main_kb import get_main_kb
from database.models.default_schedule import DefaultScheduleModel
from database.models.result_schedule import ResultScheduleModel
from database.models.users import UserModel
from database.repository import Repository
from helpers.lesson import Lesson
from services.formatter_service.schedule import (add_time_to_schedule,
                                                 format_schedule)
from services.parser_service.week import Week
from utils.constants import NO_SCHEDULE_TEXT

router = Router(name=__name__)


@router.message(F.text.lower().contains("расписание"))
async def handle_schedule(message: Message,
                          user: UserModel, repository: Repository):
    schedule = await get_schedule(user.group_id, repository)
    if user.is_time_shown:
        schedule = add_time_to_schedule(schedule)

    await message.answer(schedule,
                         reply_markup=get_main_kb(message.from_user.id))


@router.message(F.text.lower().contains("предыдущее"))
async def handle_previous_schedule(message: Message,
                                   user: UserModel, repository: Repository):
    previous_weekday = Week().get_previous_weekday()
    previous_shift = Week().get_previous_shift()

    schedule = await get_schedule(user.group_id, repository,
                                  previous_weekday, previous_shift)
    if user.is_time_shown:
        schedule = add_time_to_schedule(schedule)

    await message.answer(schedule,
                         reply_markup=get_main_kb(message.from_user.id))


@router.message(F.text.lower().contains("следующее"))
async def handle_next_schedule(message: Message,
                               user: UserModel, repository: Repository):
    next_weekday = Week().get_next_weekday()
    next_shift = Week().get_next_shift()

    schedule = await get_default_schedule(user.group_id, repository,
                                          next_weekday, next_shift)
    if user.is_time_shown:
        schedule = add_time_to_schedule(schedule)

    await message.answer(schedule,
                         reply_markup=get_main_kb(message.from_user.id))


async def get_schedule(
    group_id: int,
    repository: Repository,
    weekday: int = None,
    shift: int = None
) -> str:
    if weekday is None:
        weekday = Week().weekday
    if shift is None:
        shift = Week().shift

    result_schedule_data = await repository.result_schedule.get(weekday,
                                                                group_id)
    if validate_schedule(result_schedule_data):
        return result_schedule_data.data_lessons

    default_schedule = await get_default_schedule(
        group_id, repository, weekday, shift
    )
    return default_schedule


async def get_default_schedule(
    group_id: int,
    repository: Repository,
    weekday: int,
    shift: int
) -> str:
    default_schedule_data = await repository.default_schedule.get(
        weekday, shift, group_id
    )
    if not validate_schedule(default_schedule_data):
        return NO_SCHEDULE_TEXT

    return build_default_schedule(
        default_schedule_data,
        weekday, shift
    )


def build_default_schedule(
    default_schedule_data: DefaultScheduleModel,
    weekday: int,
    shift: int
) -> str:
    default_lessons: list[Lesson] = literal_eval(
        default_schedule_data.data_lessons
    )

    # TODO Refactoring with MRriten
    lessons = []
    for lesson in default_lessons:
        lessons.append(Lesson.from_dict(lesson))

    default_schedule = format_schedule(lessons, weekday, shift)
    return default_schedule


def validate_schedule(schedule: ResultScheduleModel | DefaultScheduleModel | None) -> bool:
    if schedule is None or schedule.data_lessons is None:
        return False

    return True
