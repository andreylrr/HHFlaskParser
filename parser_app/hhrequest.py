import requests as req

"""
     Класс HHRequest осуществляет обращение к сайту hh.ru с помощью api  
     для поиска вакансий по указанной тематики и обрабатывает 
     найденные объявления для получения списка требуемых технологий.
"""


class HHRequest():
    def __init__(self, hhparser):
        self._s_search_pattern = ""
        self._l_ignore_terms = []
        self._l_double_terms = []
        self._s_url = ""
        self._l_urls_vacancies = []
        self._o_parser = hhparser
        self.i_region_id = 0

    def set_search_pattern(self, pattern: str) -> None:
        self._s_search_pattern = pattern

    def set_url(self, url: str) -> None:
        self._s_url = url

    def set_region(self, name: str) ->None:
        j_params = {'text': name }
        j_result = req.get('https://api.hh.ru/suggests/areas', params=j_params).json()
        if j_result["items"]:
            self.i_region_id = j_result["items"][0]["id"]
        else:
            raise ValueError("Регион не найден.")

    def set_parser(self, hhparser):
        self._o_parser = hhparser

    def get_urls_vacancies(self) -> list:

        if not self._s_url:
            raise ValueError('Не задан адрес сайта.')

        if not self._s_search_pattern:
            raise ValueError('Не заданы критерии поиска.')

        if self.i_region_id == 0:
            raise ValueError('Не задан регион поиска.')

        self._s_url = self._s_url.replace('#', self.i_region_id)
        self._l_urls_vacancies.clear()

        i_page_number = 0
        while True:
            j_params = {'text': self._s_search_pattern,
                        'page': i_page_number,
                        'per_page': 100
            }

            j_result = req.get(self._s_url, params=j_params)

            if j_result.status_code != 200:
                return []

            j_result = j_result.json()
            if not j_result['items']:
                break

            for j_item in j_result['items']:
                self._l_urls_vacancies.append(j_item['url'])

            if j_result["page"] >= j_result["pages"] - 1:
                break
            else:
                i_page_number += 1

        return self._l_urls_vacancies

    def process_url(self, url: str) -> list:
        return self._o_parser.parse(req.get(url).json())


