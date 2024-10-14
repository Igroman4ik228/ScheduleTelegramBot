from bs4 import BeautifulSoup


class ElementFinder():
    def __init__(self, soup: BeautifulSoup):
        self.soup = soup

    @property
    def table(self):
        table = self.soup.find('table')
        if table is None:
            raise ValueError("Таблица отсутствует.")
        return table

    @property
    def rows(self) -> list[BeautifulSoup]:
        # skip first row (table header)
        rows = self.table.find_all('tr')[1:]
        if not rows:
            raise ValueError("Строки в таблице отсутствуют.")
        return rows

    @staticmethod
    def get_cells(row: BeautifulSoup):
        cells = row.find_all('td')
        if not cells:
            raise ValueError("Ячейки не найдены в строке таблицы.")
        return cells

    def get_text_from_div(self,
                          index: int,
                          split_by=' ',
                          word_index=-1) -> str:
        div_elements = self.soup.find_all('div')
        if index < 0 or index >= len(div_elements):
            raise IndexError(
                "Индекс выходит за пределы доступных div элементов.")

        div_element = div_elements[index]
        full_text = div_element.get_text(strip=True)
        split_text = full_text.split(split_by)

        return split_text[word_index]
