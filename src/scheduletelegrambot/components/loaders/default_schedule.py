from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from scheduletelegrambot.database.models import (
    ClassroomModel,
    DefaultScheduleAssignmentClassroomModel,
    DefaultScheduleLessonModel,
    DefaultScheduleModel,
    DefaultScheduleTeachingAssignmentModel,
    GroupModel,
    SubjectModel,
    TeacherModel,
)
from scheduletelegrambot.enums import Weekday, WeekType
from scheduletelegrambot.helpers.file import get_file_paths, load_from_json
from scheduletelegrambot.utils.constants import FILE_EXTENSION

from .paths import SCHEDULES_DIR


class InitialTeachingAssignment(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    teacher: str = Field(min_length=1)
    classrooms: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_classrooms(self):
        if any(not classroom for classroom in self.classrooms):
            raise ValueError("Кабинеты не могут быть пустыми")
        return self


class InitialLesson(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    number: int = Field(ge=0)
    subject: str = Field(min_length=1)
    teaching_assignments: list[InitialTeachingAssignment] = Field(min_length=1)


class InitialSchedule(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    groups: list[str] = Field(min_length=1)
    weeks: dict[WeekType, dict[Weekday, list[InitialLesson]]]

    @model_validator(mode="after")
    def validate_periods(self):
        if any(not group for group in self.groups):
            raise ValueError("Названия групп не могут быть пустыми")
        if len(self.groups) != len(set(self.groups)):
            raise ValueError("Группы в файле расписания должны быть уникальны")
        if set(self.weeks) != set(WeekType):
            raise ValueError("Для каждой группы должны быть оба типа недели")
        for week_type, weekdays in self.weeks.items():
            if set(weekdays) != set(Weekday):
                raise ValueError(f"Для типа недели {week_type.value} должны быть все шесть дней")
            for lessons in weekdays.values():
                numbers = [lesson.number for lesson in lessons]
                if len(numbers) != len(set(numbers)):
                    raise ValueError("Номера пар в расписании одного дня должны быть уникальны")
        return self


class DefaultScheduleLoader:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def read(self) -> list[InitialSchedule]:
        paths = get_file_paths(SCHEDULES_DIR, FILE_EXTENSION)
        if not paths:
            raise ValueError("Не найдены файлы стандартного расписания")
        schedules = [
            InitialSchedule.model_validate(await load_from_json(str(path))) for path in paths
        ]
        group_periods: set[tuple[str, WeekType, Weekday]] = set()
        for schedule in schedules:
            for group_name in schedule.groups:
                for week_type, weekdays in schedule.weeks.items():
                    for weekday in weekdays:
                        period = (group_name, week_type, weekday)
                        if period in group_periods:
                            raise ValueError(
                                "Обнаружено дублирующее расписание группы на один период"
                            )
                        group_periods.add(period)
        return schedules

    async def load(self, schedules: list[InitialSchedule], group_names: set[str]) -> bool:
        if await self._session.scalar(select(DefaultScheduleModel.id).limit(1)) is not None:
            return False

        schedule_group_names = {group for schedule in schedules for group in schedule.groups}
        unknown_groups = schedule_group_names - group_names
        if unknown_groups:
            groups_text = ", ".join(sorted(unknown_groups))
            raise ValueError(f"Расписание содержит неизвестные группы: {groups_text}")
        group_models = await self._session.scalars(
            select(GroupModel).where(GroupModel.name.in_(schedule_group_names))
        )
        groups = {group.name: group for group in group_models}
        missing_groups = schedule_group_names - set(groups)
        if missing_groups:
            groups_text = ", ".join(sorted(missing_groups))
            raise ValueError(f"Группы расписания отсутствуют в базе: {groups_text}")
        subjects, teachers, classrooms = await self._get_reference_models(schedules)
        for schedule_data in schedules:
            for group_name in schedule_data.groups:
                for week_type, weekdays in schedule_data.weeks.items():
                    for weekday, lessons in weekdays.items():
                        schedule = DefaultScheduleModel(
                            group_id=groups[group_name].id,
                            weekday=weekday,
                            week_type=week_type,
                        )
                        for lesson_data in lessons:
                            lesson = DefaultScheduleLessonModel(
                                number=lesson_data.number,
                                subject_id=subjects[lesson_data.subject].id,
                            )
                            for assignment_data in lesson_data.teaching_assignments:
                                assignment = DefaultScheduleTeachingAssignmentModel(
                                    teacher_id=teachers[assignment_data.teacher].id
                                )
                                assignment.classrooms = [
                                    DefaultScheduleAssignmentClassroomModel(
                                        classroom_id=classrooms[classroom].id
                                    )
                                    for classroom in assignment_data.classrooms
                                ]
                                lesson.teaching_assignments.append(assignment)
                            schedule.lessons.append(lesson)
                        self._session.add(schedule)
        await self._session.flush()
        return True

    async def ensure_consistent_state(self) -> None:
        has_schedules = await self._session.scalar(select(DefaultScheduleModel.id).limit(1))
        has_children = any(
            [
                await self._session.scalar(select(DefaultScheduleLessonModel.id).limit(1)),
                await self._session.scalar(
                    select(DefaultScheduleTeachingAssignmentModel.id).limit(1)
                ),
                await self._session.scalar(
                    select(DefaultScheduleAssignmentClassroomModel.id).limit(1)
                ),
            ]
        )
        if has_children and not has_schedules:
            raise RuntimeError(
                "Обнаружены дочерние элементы расписания без стандартного расписания"
            )

    async def _get_reference_models(
        self, schedules: list[InitialSchedule]
    ) -> tuple[dict[str, SubjectModel], dict[str, TeacherModel], dict[str, ClassroomModel]]:
        subject_names = {
            lesson.subject
            for schedule in schedules
            for weekdays in schedule.weeks.values()
            for lessons in weekdays.values()
            for lesson in lessons
        }
        teacher_names = {
            assignment.teacher
            for schedule in schedules
            for weekdays in schedule.weeks.values()
            for lessons in weekdays.values()
            for lesson in lessons
            for assignment in lesson.teaching_assignments
        }
        classroom_names = {
            classroom
            for schedule in schedules
            for weekdays in schedule.weeks.values()
            for lessons in weekdays.values()
            for lesson in lessons
            for assignment in lesson.teaching_assignments
            for classroom in assignment.classrooms
        }
        subjects = await self._get_models_by_name(SubjectModel, subject_names)
        teachers = await self._get_models_by_name(TeacherModel, teacher_names)
        classrooms = await self._get_models_by_name(ClassroomModel, classroom_names)
        return subjects, teachers, classrooms

    async def _get_models_by_name[TModel: SubjectModel | TeacherModel | ClassroomModel](
        self, model: type[TModel], names: set[str]
    ) -> dict[str, TModel]:
        models = list(await self._session.scalars(select(model).where(model.name.in_(names))))
        existing_names = {model.name for model in models}
        models.extend(model(name=name) for name in names - existing_names)
        self._session.add_all(models[len(existing_names) :])
        await self._session.flush()
        return {model.name: model for model in models}
