import logging
from datetime import time as dt_time

from bs4 import BeautifulSoup

import utils.constants as const
from services.parser_service.lesson import Lesson
from services.parser_service.week import Week
from utils.different import get_key

# class HtmlParser:

#     def __init__(self, html_content: str):
#         self.soup = BeautifulSoup(html_content, 'lxml')

#     @property
#     def table(self) -> BeautifulSoup:
#         """Получение таблицы"""
#         table = self.soup.find('table')
#         if table is None:
#             raise ValueError("Таблица отсутствует.")
#         return table

#     @property
#     def table_rows(self) -> list[BeautifulSoup]:
#         """Получение строк таблицы (пропускаем заголовок)"""
#         rows = self.table.find_all('tr')[1:]
#         if not rows:
#             raise ValueError("Строки в таблице отсутствуют.")
#         return rows

#     @property
#     def div_elements(self):
#         """Получение всех div элементов"""
#         return self.soup.find_all('div')

#     def initialize_week(self):
#         """Инициализация значения Week (Singleton)"""
#         weekday = self._get_weekday()
#         shift = self._get_shift()
#         Week().initialize(weekday, shift)

#     def _get_weekday(self) -> int:
#         """Извлекает день недели из HTML"""
#         weekday_name = self.get_text_from_div(index=2).strip().lower()
#         weekday = get_key(const.DAY_NAMES, weekday_name)
#         if weekday is None:
#             raise ValueError(
#                 f"Не удалось определить день недели: {weekday_name}"
#             )
#         return weekday

#     def _get_shift(self) -> int:
#         """Извлекает информацию о смене (числитель/знаменатель) из HTML"""
#         shift_name = self.get_text_from_div(index=3,
#                                             word_index=0).strip("()").lower()
#         shift = const.WEEK_SCHEDULE_MAPPING.get(shift_name)
#         if shift is None:
#             raise ValueError(
#                 "Не удалось определить числитель/знаменатель. "
#                 f"Значение: {shift_name}"
#             )
#         return shift

#     # Парсинг расписания замены
#     def extract_replacement_schedule(self) -> dict[str, list[Lesson]]:
#         replacement_schedule = {}
#         rows = self.get_table_rows()

#         for row in rows:
#             cells = self.get_cells(row)
#             group = self._parse_group(cells)
#             if group is None:
#                 continue

#             replacement_lessons = self._parse_replacement_lessons(cells)
#             replacement_schedule.setdefault(
#                 group, []
#             ).extend(replacement_lessons)

#         return replacement_schedule

#     # Получение таблицы
#     def get_table(self):
#         table = self.soup.find('table')
#         if table is None:
#             raise ValueError("Таблица отсутствует.")
#         return table

#     # Получение строк таблицы (пропускаем заголовок)
#     def get_table_rows(self) -> list[BeautifulSoup]:
#         rows = self.get_table().find_all('tr')[1:]
#         if not rows:
#             raise ValueError("Строки в таблице отсутствуют.")
#         return rows

#     # Получение ячеек строки таблицы
#     def get_cells(self, row: BeautifulSoup):
#         cells = row.find_all('td')
#         if not cells:
#             raise ValueError("Ячейки не найдены в строке таблицы.")
#         return cells

#     # Получение текста из div элементов
#     def get_text_from_div(self, index: int, split_by=' ', word_index=-1) -> str:
#         div_elements = self.soup.find_all('div')
#         if index < 0 or index >= len(div_elements):
#             raise IndexError(
#                 "Индекс выходит за пределы доступных div элементов.")
#         div_element = div_elements[index]
#         full_text = div_element.get_text(strip=True)
#         split_text = full_text.split(split_by)
#         return split_text[word_index]

#     # Вспомогательные методы для парсинга расписания
#     def _parse_replacement_lessons(self, cells: BeautifulSoup) -> list[Lesson]:
#         lesson_numbers, time = self._get_lesson_numbers(cells[2].text.strip())
#         subject = cells[4].text.strip()
#         classrooms = cells[5].text.strip()

# replacement_lessons = []
# for lesson_number in lesson_numbers:
#     replacement_lessons.append(
#         Lesson(lesson_number, time, subject,
#                classrooms, is_replacement=True)
#     )

# return replacement_lessons

#     def _parse_group(self, cells: BeautifulSoup) -> str | None:
#         group = cells[1].text.strip().upper()
#         return group if group else None

#     def _get_lesson_numbers(self, lesson_numbers: str) -> tuple[list[int], dt_time | None]:
#         if ',' in lesson_numbers:
#             return self._parse_comma_separated(lesson_numbers), None
#         if '-' in lesson_numbers:
#             return self._parse_range(lesson_numbers), None
#         if lesson_numbers.count('.') == 1:
#             return self._parse_time_format(lesson_numbers)
#         if lesson_numbers.isdigit():
#             return [int(lesson_numbers)], None
#         if lesson_numbers == "":
#             return self._parse_default_numbers(), None

#         raise ValueError("Неправильный формат номера замены: "
#                          f"{lesson_numbers}")

#     def _parse_range(self, lesson_numbers: str) -> list[int]:
#         start, end = map(int, lesson_numbers.split('-'))
#         return list(range(start, end + 1))

#     def _parse_comma_separated(self, lesson_numbers: str) -> list[int]:
#         return [int(number.strip()) for number in lesson_numbers.split(',')]

#     def _parse_time_format(self, lesson_numbers_string: str) -> tuple[list[int], dt_time]:
#         hour_str, minute_str = lesson_numbers_string.split('.')
#         time = dt_time(int(hour_str), int(minute_str))
#         lesson_number = Lesson.get_lesson_number_by_time(time)
#         return [lesson_number], time

#     def _parse_default_numbers(self) -> list[int]:
#         return list(range(len(const.START_LESSONS_TIME)))


class HtmlParser:
    def __init__(self, html_content: str):
        self.soup = BeautifulSoup(html_content, 'lxml')

    @property
    def table(self) -> BeautifulSoup:
        """Получение таблицы"""
        table = self.soup.find('table')
        if table is None:
            raise ValueError("Таблица отсутствует.")
        return table

    @property
    def table_rows(self) -> list[BeautifulSoup]:
        """Получение строк таблицы (пропускаем заголовок)"""
        rows = self.table.find_all('tr')[1:]
        if not rows:
            raise ValueError("Строки в таблице отсутствуют.")
        return rows

    @property
    def div_elements(self) -> list[BeautifulSoup]:
        """Получение всех div элементов"""
        return self.soup.find_all('div')

    def initialize_week(self):
        """Инициализация значения Week (Singleton)"""
        weekday = self._get_weekday()
        shift = self._get_shift()
        Week().initialize(weekday, shift)

    def _get_weekday(self) -> int:
        """Извлекает день недели из HTML"""
        weekday_name = self.get_text_from_div(index=2).strip().lower()
        weekday = get_key(const.DAY_NAMES, weekday_name)
        if weekday is None:
            raise ValueError(
                f"Не удалось определить день недели: {weekday_name}")
        return weekday

    def _get_shift(self) -> int:
        """Извлекает информацию о смене (числитель/знаменатель) из HTML"""
        shift_name = self.get_text_from_div(
            index=3, word_index=0).strip("()").lower()
        shift = const.WEEK_SCHEDULE_MAPPING.get(shift_name)
        if shift is None:
            raise ValueError(
                f"Не удалось определить числитель/знаменатель. Значение: {shift_name}")
        return shift

    def extract_replacement_schedule(self) -> dict[str, list[Lesson]]:
        """Парсинг расписания замены"""
        replacement_schedule = {}
        for row in self.table_rows:
            cells = self.get_cells(row)
            group = self._parse_group(cells)
            if not group:
                continue

            replacement_lessons = self._parse_replacement_lessons(cells)
            replacement_schedule.setdefault(
                group, []
            ).extend(replacement_lessons)

        return replacement_schedule

    def get_cells(self, row: BeautifulSoup) -> list[BeautifulSoup]:
        """Получение ячеек строки таблицы"""
        cells = row.find_all('td')
        if not cells:
            raise ValueError("Ячейки не найдены в строке таблицы.")

        return cells

    def get_text_from_div(self, index: int, split_by: str = ' ', word_index: int = -1) -> str:
        """Получение текста из div элементов"""
        if index < 0 or index >= len(self.div_elements):
            raise IndexError(
                "Индекс выходит за пределы доступных div элементов.")
        div_element = self.div_elements[index]
        split_text = div_element.get_text(strip=True).split(split_by)

        return split_text[word_index]

    def _parse_replacement_lessons(self, cells: list[BeautifulSoup]) -> list[Lesson]:
        """Парсинг заменяемых уроков"""
        lesson_numbers, time = self._get_lesson_numbers(cells[2].text.strip())
        subject = cells[4].text.strip()
        classrooms = cells[5].text.strip()

        replacement_lessons = []
        for lesson_number in lesson_numbers:
            replacement_lessons.append(
                Lesson(lesson_number, time, subject,
                       classrooms, is_replacement=True)
            )

        return replacement_lessons

    def _parse_group(self, cells: list[BeautifulSoup]) -> str | None:
        """Парсинг группы"""
        group = cells[1].text.strip().upper()
        return group if group else None

    def _get_lesson_numbers(self, lesson_numbers: str) -> tuple[list[int], dt_time | None]:
        """Получение номеров уроков и времени"""
        if ',' in lesson_numbers:
            return self._parse_comma_separated(lesson_numbers), None
        if '-' in lesson_numbers:
            return self._parse_range(lesson_numbers), None
        if lesson_numbers.count('.') == 1:
            return self._parse_time_format(lesson_numbers)
        if lesson_numbers.isdigit():
            return [int(lesson_numbers)], None
        if lesson_numbers == "":
            return self._parse_default_numbers(), None

        raise ValueError(
            f"Неправильный формат номера замены: {lesson_numbers}"
        )

    def _parse_range(self, lesson_numbers: str) -> list[int]:
        """Парсинг диапазона номеров уроков"""
        start, end = map(int, lesson_numbers.split('-'))
        return list(range(start, end + 1))

    def _parse_comma_separated(self, lesson_numbers: str) -> list[int]:
        """Парсинг номеров уроков, разделённых запятыми"""
        return [int(number.strip()) for number in lesson_numbers.split(',')]

    def _parse_time_format(self, lesson_numbers_string: str) -> tuple[list[int], dt_time]:
        """Парсинг времени в формате HH.MM"""
        hour_str, minute_str = lesson_numbers_string.split('.')
        time = dt_time(int(hour_str), int(minute_str))
        lesson_number = Lesson.get_lesson_number_by_time(time)
        return [lesson_number], time

    def _parse_default_numbers(self) -> list[int]:
        """Получение номеров по умолчанию"""
        return list(range(len(const.START_LESSONS_TIME)))
