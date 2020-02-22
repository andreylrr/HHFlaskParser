from web_app import models
from web_app import database

if __name__ == "__main__":
    # Запросить у пользователя, нужно ли создать новую БД, удалив старую
    if input("Создать новую БД? Y/N:") == "Y":
        try:
            database.create_db()
            print("БД успешно обновлена")
        except Exception as ex:
            print(f"Произошла ошибка при создании БД. {ex}")
