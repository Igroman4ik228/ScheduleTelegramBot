from bs4 import BeautifulSoup

import constants


class ElementFinder():
    def __init__(self, soup: BeautifulSoup):
        self.soup = soup
        self.table = self._get_table()
        self.rows = self._get_rows()

    def _get_table(self):
        table = self.soup.find('table')
        if table is None:
            raise ValueError("Таблица отсутствует.")
        return table

    def _get_rows(self) -> list[BeautifulSoup]:
        return self.table.find_all('tr')[1:]

    @staticmethod
    def get_cells(row: BeautifulSoup):
        return row.find_all('td')

    def get_text_from_div(self,
                          index: int,
                          split_by=' ',
                          split_index=-1) -> str:
        div_elements = self.soup.find_all('div')
        if index < 0 or index >= len(div_elements):
            raise IndexError(
                "Индекс выходит за пределы доступных div элементов.")

        div_element = div_elements[index]
        full_text = div_element.get_text(strip=True)
        split_text = full_text.split(split_by)

        return split_text[split_index]

    def get_weekday(self) -> int:
        day_of_week_name = self.get_text_from_div(index=2).lower()
        day_of_week = get_key(constants.DAY_NAMES, day_of_week_name)

        return day_of_week

    def get_shift(self) -> int:
        week_schedule_name = self.get_text_from_div(index=3, split_index=0)
        week_schedule_name = week_schedule_name.strip("()").lower()

        week_schedule = constants.WEEK_SCHEDULE_MAPPING.get(week_schedule_name)

        if week_schedule is None:
            raise ValueError(
                f"Не удалось определить числитель/знаменатель. Значение: {week_schedule_name}")

        return week_schedule


def get_key(input_dict: dict, target_value):
    for key, value in input_dict.items():
        if value == target_value:
            return key
    raise ValueError(f"{target_value} не найден в {input_dict}")
