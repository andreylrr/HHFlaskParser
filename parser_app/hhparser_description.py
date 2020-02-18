import re
import json
#
#   HHParserDescription класс предназначен для обработки описаний вакансий полученных с сайта hh.ru
#   В каждом описании вакансии парсер определяет какие технологии были востребованы и
#   возвращает их список
#

class HHParserDescription():
    def __init__(self):
        self._l_found_technology = []
        self._s_description = ""
        self._l_ignore_terms = []
        self._l_double_terms = []

    def parse(self, vacancy: json) -> list:
        """
            Основной метод обработки вакансии
        :param vacancy: Вакансия представленная в json формате
        :return: список найденных терминов
        """
        self._s_description = vacancy['description']
        self._clean_trash()
        self._clean_html()
        self._find_technology()
        return self._l_found_technology

    def _clean_trash(self) -> None:
        """
            Метод для очистки описания от символов, которые на являются буквами английского алфавита
        """
        re_cleanr = re.compile('^[A-Za-z0-9]+')
        self._s_description = re_cleanr.sub(" ", self._s_description )
        self._s_description = self._s_description.replace(",", "")
        self._s_description = self._s_description.replace(";", "")
        self._s_description = self._s_description.replace(")", "")
        self._s_description = self._s_description.replace("(", "")
        self._s_description = self._s_description.replace("«", "")
        self._s_description = self._s_description.replace("»", "")
        self._s_description = self._s_description.replace("!", "")


    def _clean_html(self) -> None:
        """
            Метод для очистки описания от html тагов
        """
        re_cleanr = re.compile('<.*?>')
        self._s_description = re.sub(re_cleanr, '', self._s_description)

    def _find_technology(self) -> None:
        """
            Метод для определения ключевых слов по технологиям
        :return:
        """
        # Убираем русский текст
        l_tech = self._s_description.split()
        self._l_found_technology = [word for word in l_tech if not re.match("[А-Яа-я]", word)]

        # Убираем слова, которые не начинаются с большой буквы
        self._l_found_technology = [word for word in self._l_found_technology if word.istitle()]
        # Собираем термины, состоящие из двух слов
        self._l_found_technology = self._process_double_terms(self._l_found_technology)
        # Убираем слова, присутствующие в файле ignore
        self._l_found_technology = self._clean_ignore_terms(self._l_found_technology)
        # Убираем повторы
        self._l_found_technology = list(set(self._l_found_technology))

    def _clean_ignore_terms(self, terms: list) -> list:
        """
            Метод удаления мусорных слов из окончательного списка терминов
        :param terms: Список терминов
        :return: Очищенный список терминов
        """
        # Если список мусорных слов пуст, то возвращаем изначальный список слов
        if not self._l_ignore_terms:
            return terms

        # Очищаем список от мусорных слов
        l_result = terms.copy()
        l_result = [term for term in l_result if term not in self._l_ignore_terms]
        return l_result

    def _process_double_terms(self, terms: list) -> list:
        """
            Метод нахождения двойных терминов в списке
        :param terms: Список терминов
        :return: Преобразованный список терминов
        """

        # Если список с терминами из двух слов пуст,
        # то возвращаем начальный список
        if not self._l_double_terms:
            return terms

        # Преобразуем список с учетом двойных терминов
        l_result_double = []
        s_result = " ".join(terms)
        for double_term in self._l_double_terms:
            if double_term in s_result:
                l_result_double.append(double_term)
                s_result = s_result.replace(double_term, " ")
        l_result = s_result.split(" ")
        l_result.extend(l_result_double)
        return l_result


    def load_help_files(self, file_ignore: str, file_double: str) -> None:
        """
             Метод загрузки двух вспомогательных файлов.

        :param file_ignore: Имя файла с терминами, которые надо игнорировать
        :param file_double: Имя файла с терминами, состоящими из двух слов
        :return:
        """

        # Открываем файл с терминами, которые надо игнорировать
        try:
            with open(file_ignore,"r") as f:
                for ignore_term in f:
                    self._l_ignore_terms.append(ignore_term.replace("\n",""))
        except FileNotFoundError:
            self._l_ignore_terms = []

        # Открываем файл с терминами, состоящими из двух слов
        try:
            with open(file_double, "r") as f:
                for double_term in f:
                    self._l_double_terms.append(double_term.replace("\n",""))
        except FileNotFoundError:
            self._l_double_terms = []


if __name__ == '__main__':
    pass
