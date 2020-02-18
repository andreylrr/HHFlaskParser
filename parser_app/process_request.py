import hhrequest as hr
import hhparser_description as hp
import hhparser_key_skills as hk
import hhparser_salary as hs
import requests as req
import configparser as cfg
import sqlite3 as sql
import time
import json


def add_skills(sum_skills: dict, skills_to_add: list):
    for s_skill in skills_to_add:
        if s_skill in sum_skills:
            sum_skills[s_skill] += 1
        else:
            sum_skills[s_skill] = 1


def sort_skills(skills: dict, vacancies_number: int) -> dict:
    d_sorted: dict = dict(sorted(skills.items(), key=lambda x: x[1], reverse=True))
    for key, value in d_sorted.items():
        d_sorted[key] = round((value / vacancies_number) * 100, 2)
    return d_sorted


def process_salary(all_salary: dict, salary: list) -> dict:
    """
         Функция обработки списка с зарплатой
    :param all_salary - словарь с результатами парсинга всех страниц
           salary: элемент списка с зарплатой
    """
    if salary:
        all_salary[salary[0]] = [all_salary[salary[0]][0] + salary[1],
                                 all_salary[salary[0]][1] + salary[2],
                                 all_salary[salary[0]][2] + 1]
    return all_salary


def avg_salary(all_salary: dict) -> dict:
    """
        Функция обработки всех найденных зарплат
    :param all_salary: словарь с зарплатами и количеством вакансий
    :return:  обработанный словарь
    """
    # Вычисляем среднее значение зарплат по разным категориям
    if all_salary['Senior'][2] != 0:
        all_salary["Senior"] = [all_salary['Senior'][0] / all_salary['Senior'][2],
                                all_salary['Senior'][1] / all_salary['Senior'][2]]
    if all_salary['Middle'][2] != 0:
        all_salary["Middle"] = [all_salary['Middle'][0] / all_salary['Middle'][2],
                                all_salary['Middle'][1] / all_salary['Middle'][2]]
    if all_salary['Junior'][2] != 0:
        all_salary["Junior"] = [all_salary['Junior'][0] / all_salary['Junior'][2],
                                all_salary['Junior'][1] / all_salary['Junior'][2]]
    if all_salary['Unknown'][2] != 0:
        all_salary["Unknown"] = [all_salary['Unknown'][0] / all_salary['Unknown'][2],
                                 all_salary['Unknown'][1] / all_salary['Unknown'][2]]
    return all_salary


def process_request(db_path, file_folder, db_row):
    '''
        Функция обработки запроса, прочитанного из БД
    :param db_path: путь к БД
    :param file_folder: путь к файлам с результатами
    :param db_row: запрос, прочитанный из БД
    '''

    # Меняем статус на "В обработке"
    update_status(db_path, db_row, 1)
    # Задаем начальные значения поиска
    s_url = 'https://api.hh.ru/vacancies?area=#'

    # Создаем парсеры для извлечения информации
    o_pars_description = hp.HHParserDescription()
    o_pars_salary = hs.HHParserSalary()
    o_pars_key_skills = hk.HHParserKeySkills()

    # Загружаем вспомогательные файлы для парсера описаний вакансий
    o_pars_description.load_help_files("ignore_terms.txt", "double_terms.txt")

    # Создаем класс для работы с парсерами
    o_hhrequest = hr.HHRequest(o_pars_description)
    o_hhrequest.set_url(s_url)

    # Запрашиваем регион поиска у пользователя
    o_hhrequest.set_region(db_row[1])

    # Передаем строку поиска управляющему классу
    o_hhrequest.set_search_pattern(db_row[2])

    # Получаем список urls вакансий, удовлетворяющих критерию поиска
    l_urls = o_hhrequest.get_urls_vacancies()

    if not l_urls:
        update_status(db_path, db_row, 2)
        print("По Вашему запросу вакансий не найдено")
    else:
        i_number_vacancies = 0
        d_description: dict = dict()
        d_key_skills: dict = dict()
        d_salary: dict = {"Junior": [0, 0, 0],
                          "Middle": [0, 0, 0],
                          "Senior": [0, 0, 0],
                          "Unknown": [0, 0, 0], }
        l_salary: list = list()
        # Парсим список ссылок на страницы вакансий
        for s_url in l_urls:
            # Получаем страницу вакансии
            j_vacancy = req.get(s_url).json()
            # Добавляем навыки извлеченные из описания и ключевых навыков
            add_skills(d_description, o_pars_description.parse(j_vacancy))
            add_skills(d_key_skills, o_pars_key_skills.parse(j_vacancy))
            # Обрабатываем зарплату
            l_salary = o_pars_salary.parse(j_vacancy)
            if l_salary:
                process_salary(d_salary, l_salary)
            i_number_vacancies += 1

        # Сортируем навыки по частоте упоминаний
        d_skills_sorted = sort_skills(d_key_skills, i_number_vacancies)
        d_skills_description_sorted = sort_skills(d_description, i_number_vacancies)
        # Усредняем зарплату
        d_salary = avg_salary(d_salary)

        # Формируем словарь с навыками и зарплатой
        d_sum: dict = {"salary": d_salary, "description": d_skills_description_sorted, "keyskills": d_skills_sorted}

        # Записываем словарь в формате json в файл, в указанный каталог
        file_name: str = str(db_row[0]) + "-" + db_row[1] + "-" + time.strftime("%Y%m%d%H%M", time.localtime())
        with open(file_folder + "/" + file_name, "w") as f:
            json.dump(d_sum, f)
        # Обновляем запись с результатами запроса
        update_request(db_path, db_row, file_name, i_number_vacancies)


def read_requests(db_path):
    """
         Функция чтения запросов из БД
    :param db_path: путь к БД
    :return: список найденных записей
    """
    try:
        # Устанавливаем связь с БД
        db_connection = sql.connect(db_path)
        cursor = db_connection.cursor()
    except Exception as ex:
        print(f"Error during establishing connection to DB\n{ex}")
        return

    # Выбираем все запросу для данного пользователя из БД
    sql_statement: str = '''SELECT user_id, region, text_request, id from requests where status = 0'''
    cursor.execute(sql_statement)
    row = cursor.fetchall()
    # Закрываем связь с БД
    cursor.close()
    db_connection.close()
    return row


def update_request(db_path, db_row, file_name, number_vacancies):
    """
        Функция обновления записи запроса в БД
    :param db_path: путь к БД
    :param db_row: запись, которую надо обновить
    :param file_name: имя файла с результатами
    :param number_vacancies: количество вакансий
    """
    try:
        # Устанавливаем связь с БД
        db_connection = sql.connect(db_path)
        cursor = db_connection.cursor()
    except Exception as ex:
        print(f"Error during establishing connection to DB\n{ex}")
        return

    # Формируем запрос к БД
    sql_statement: str = '''UPDATE requests SET file_name = ?, vacancy_number = ?, status = 2,''' \
                         '''updated=datetime('now', 'localtime') WHERE id = ?'''
    cursor.execute(sql_statement, (file_name, number_vacancies, db_row[3]))
    db_connection.commit()
    # Закрываем связь с БД
    cursor.close()
    db_connection.close()


def update_status(db_path, db_row, status):
    """
        Функция изменеия статуса запроса в БД
    :param db_path: путь к БД
    :param db_row: запись, статус в которой надо обновить
    :param status: статус
    """
    try:
        # Устанавливаем связь с БД
        db_connection = sql.connect(db_path)
        cursor = db_connection.cursor()
    except Exception as ex:
        print(f"Error during establishing connection to DB\n{ex}")
        return

    # Если статус меняется на один (В обработке), то не надо изменять кол-во вакансий
    if status == 1:
        sql_statement: str = '''UPDATE requests SET status = ?, updated=datetime('now', 'localtime') WHERE id = ?'''
    else:
        sql_statement: str = '''UPDATE requests SET status = ?, vacancy_number = 0, updated=datetime('now','local')WHERE id = ? '''

    cursor.execute(sql_statement, (status, db_row[3]))
    db_connection.commit()
    # Закрываем связь с БД
    cursor.close()
    db_connection.close()


if __name__ == '__main__':

    # Читаем конфигурационные параметры
    config = cfg.ConfigParser()
    config.read("hh_config.ini")
    sqlite_db = config["SQLite"]["path"]
    file_folder = config["Json"]["path"]

    while True:
        # Читаем записи со статусом 0 из БД
        rows = read_requests(sqlite_db)
        if rows:
            # Если записи найдены, то начинаем обработку
            for row in rows:
                print(f"Обработка запроса: {row[1]} {row[2]} начата.")
                process_request(sqlite_db, file_folder, row)
                print(f"Обработка запроса: {row[1]} {row[2]} завершена.")
        else:
            # Переходим в режим ожидания
            time.sleep(5)
            print("Новых запросов не найдено.")
