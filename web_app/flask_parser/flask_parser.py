from flask import Blueprint, render_template, request, session, g, redirect, flash
import parser_app.hhrequest as hr
from flask_table import Table, Col, LinkCol
import json

parser_blueprint = Blueprint("flask_parser", __name__)

# Создание таблицы для вывода на странице История
class ItemTable(Table):
    # Атрибуты таблицы, которые будут использованы при ввыоде ее на экран
    classes = ["table", "table-bordered"]
    tab_id = Col("Номер запроса")
    region = Col('Регион')
    text_request = Col('Запрос')
    vacancies_numbers = Col("Кол-во вакансий")
    status = Col("Статус")
    created = Col("Создан")
    name = LinkCol('Смотреть', 'flask_parser.single_item',
                         url_kwargs=dict(id='tab_id'))


@parser_blueprint.route("/")
def root():
    """
       Функция обработки запроса к корневой странице
    :return Страница Index
    """
    return render_template("index.html")


@parser_blueprint.route("/index")
def index():
    """
       Функция обработки запроса к странице Index
    :return Страница Index
    """
    return render_template("index.html")


@parser_blueprint.route("/history")
def history():
    """
        Функция обработки запроса к странице История
    :return:
    """
    # Если пользователь не авторизовался, то возвращаем его к странице авторизации
    if session.get("user_id"):
        # Читаем из БД список запросов
        items = Item.get_elements()
        # Формируем таблицу
        table = ItemTable(items)
        # Возвращаем страницу с интегрированной таблицей
        return render_template("history.html", tables=table)
    else:
        return redirect("login")

@parser_blueprint.route("/item/<int:id>",methods=["GET", "POST"])
def single_item(id):
    # Эта страница доступна только для авторизованного пользователя
    if session["user_id"]:
        # Достаем из списка требуемый элемент
        element = Item.get_element_by_id(id)
        # Достаем из БД имя файла с результатами обработки запроса
        cur = g.db.cursor()
        sql = "SELECT file_name FROM requests WHERE id = ?"
        cur.execute(sql, (element.request_id,))
        row = cur.fetchone()
        # Читаем результаты обработки запроса из файла
        with open(row[0], "r") as f:
            result: json = json.load(f)
        # Обрабатываем результаты запроса
        description_skills: dict = result['description']
        key_skills: dict = result['keyskills']
        salary_average: dict = result['salary']
        # Для навыков из описания
        sum_description: list = []
        for key, value in list(description_skills.items())[:10]:
            sum_description.append( key + " - " + str(value) + "%")
        # Для навыков из ключевых навыков
        sum_keyskills: list = []
        for key, value in list(key_skills.items())[:10]:
            sum_keyskills.append(key + " - " + str(value) + "%")
        sum_salaries: list = []
        # Для зарплат
        for key, value in salary_average.items():
            sum_salaries.append(key + "   от: " + '{:6.0f}'.format(value[0]) + "₽.  до: " + '{:6.0f}'.format(value[1]) + "₽.")

        # Возвращаем страницу с результатами запроса
        return render_template("request-view.html", description=sum_description,
                               keyskills=sum_keyskills, salaries=sum_salaries)
    else:
        return redirect("/login")

class Item(object):
    """
        Класс описывающий элемент таблицы
    """
    def __init__(self, tab_id, req_id, region, text_request, status, vac_number, created):
        self.tab_id = tab_id
        self.request_id = req_id
        self.region = region
        self.text_request = text_request
        self.vacancies_numbers = vac_number
        self.status = status
        self.created = created

    @classmethod
    def get_elements(cls):
        """
            Метод для получения списка запросов из БД
        :return: список запросов
        """
        # Читаем из БД список запросов для текущего пользователя
        cur = g.db.cursor()
        sql = "SELECT id, region, text_request, file_name, status, created, vacancy_number FROM requests WHERE user_id = ? ORDER BY created desc"
        cur.execute(sql, (session["user_id"],))
        rows = cur.fetchall()
        id_n = 1
        items_for_table = []
        # Обрабатываем полученный список
        for row in rows:
            # Вместо None устанавливаем количество вакансий в 0
            vac_numbers = row[6]
            if not row[6]:
                vac_numbers = 0
            # Обрабатываем статус запроса
            if row[4] == 0:
                status = 'Инициализирован'
            elif row[4] == 1:
                status = "В обработке"
            elif row[4] == 2:
                status = "Завершен"
            else:
                status = "Неопределен"
            # Добавляем элемент в таблицу
            items_for_table.append(Item(id_n, row[0], row[1], row[2], status, vac_numbers, row[5]))
            id_n += 1
        return items_for_table

    @classmethod
    def get_element_by_id(cls, id):
        """
            Получаем конкретный элемент из таблицы
        :param id: номер требуемего элемента
        :return: элемент из таблицы
        """
        return [i for i in cls.get_elements() if i.tab_id == id][0]


@parser_blueprint.route("/requests", methods=["GET","POST"])
def requests():
    """
        Функция обработки запроса к странице Запросы
    :return: Обработанную страницу Запросы
    """
    # Эта страница доступна только авторизованному пользователю
    if session.get("user_id"):
        # Обработка формы по запросу
        if request.method == "POST":
            # Достаем нужные данные из формы запроса
            region = request.form["Region"]
            text_request = request.form["Request"]
            o_hhrequest = hr.HHRequest(None)
            try:
                # Проверяем правильность задания региона
                j_result = o_hhrequest.set_region(region)
            except ValueError as ex:
                flash("Регион указан не правильно")
                return render_template("requests.html")
            # Берем регион из проверки
            region = j_result["items"][0]["text"]
            # Вставляем запрос в БД для обработки
            cur = g.db.cursor()
            sql = "INSERT INTO requests (user_id,region,text_request,status,created) VALUES (?,?,?,?, datetime('now', 'localtime'))"
            cur.execute(sql,(session["user_id"], region, text_request,0))
            g.db.commit()
            flash("Запрос отправлен на обработку. Его состояние можно отслеживать в истории.")
    else:
        # Если пользователь не авторизован то отправляем его в Login
        return redirect("login")
    return render_template("requests.html")
