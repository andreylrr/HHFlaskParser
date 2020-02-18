import json
import re
#
#   HHParserSalary класс предназначен для вакансий полученных с сайта hh.ru
#   В каждой вакансии парсер определяет зарплаты, если они указаны
#

class HHParserSalary():
    def __init__(self):
        self._l_found_salary = []
        self._s_type_vacancy = ""

    def parse(self, vacancy: json) -> list:
        self._get_vacancy_type(vacancy['description'])
        self._get_vacancy_type(vacancy['name'])

        if vacancy['salary']:
            if vacancy['salary']['currency'] == "EUR":
                f_coeff = 69.0
            elif vacancy['salary']['currency'] == "USD":
                f_coeff = 62.0
            else:
                f_coeff = 1.0

            if vacancy['salary']['from'] is None:
                f_from = vacancy['salary']['to']
                f_to = f_from
            elif vacancy['salary']['to'] is None:
                f_to = vacancy['salary']['from']
                f_from = f_to
            else:
                f_from = vacancy['salary']['from']
                f_to = vacancy['salary']['to']

            return [self._s_type_vacancy,
                    f_from * f_coeff,
                    f_to * f_coeff]
        return []

    def _get_vacancy_type(self, vacancy: str):
        self._l_found_salary = []
        vac_descr: str = vacancy.lower()
        if re.search(r"senior|ведущий|старший", vac_descr):
            self._s_type_vacancy = "Senior"
        elif re.search(r"junior|младший|ученик", vac_descr):
            self._s_type_vacancy = "Junior"
        elif re.search(r"middle|опытный", vac_descr):
            self._s_type_vacancy = "Middle"
        else:
            self._s_type_vacancy = "Unknown"


if __name__ == '__main__':
    pass
