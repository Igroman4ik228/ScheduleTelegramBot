from bs4 import BeautifulSoup


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
                          word_index=-1) -> str:
        div_elements = self.soup.find_all('div')
        if index < 0 or index >= len(div_elements):
            raise IndexError(
                "Индекс выходит за пределы доступных div элементов.")

        div_element = div_elements[index]
        full_text = div_element.get_text(strip=True)
        split_text = full_text.split(split_by)

        return split_text[word_index]
