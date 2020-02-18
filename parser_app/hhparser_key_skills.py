import json
#
#   HHParserKeySkills класс предназначен для обработки описаний вакансий полученных с сайта hh.ru
#   В каждом описании вакансии парсер определяет какие технологии были востребованы и
#   возвращает их список
#

class HHParserKeySkills():
    def __init__(self):
        self._l_found_technology = []

    def parse(self, vacancy: json) -> list:
        self._l_found_technology = []
        self._l_skills = vacancy['key_skills']
        if self._l_skills:
            self._find_technology()
        else:
            self._l_found_technology = []
        return list(set(self._l_found_technology))

    def _find_technology(self) -> None:
        """
            Метод для определения ключевых слов по технологиям
        :return:
        """
        for tec_dic in self._l_skills:
            self._l_found_technology.append(tec_dic["name"])

if __name__ == '__main__':
    pass
