import sqlite3
from datetime import datetime

# Функция получения имён и количества таблиц в базе
def names_tables(data_base):
    try:
        connection = sqlite3.connect(data_base)  # Подключение к БД
        cursor = connection.cursor()             # Создание курсора
        qwery_name_tables = 'SELECT name from sqlite_master where type="table"'  # Запрос на получение имён таблиц в БД
        cursor.execute(qwery_name_tables)        # Выполнение запроса имён таблиц
        names_tables = cursor.fetchall()         # Массив имён таблиц
        cursor.close()                           # Закрытие курсора
        connection.close()                       # Закрытие соединения с БД
        return names_tables, len(names_tables)   # Функция возвращает котртеж([имена таблиц], количество сторбцов)
    except:
        return False

# Функция получения имён столбцов в таблице базы
def names_columns(data_base, table):
    try:
        connection = sqlite3.connect(data_base)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute(f"select * from '{table}'")
        line = cursor.fetchone()
        names_column = line.keys()
        cursor.close()
        connection.close()
        return names_column
    except:
        return False

# Функция получения информации из базы
def load_data(data_base, table):
    try:
        connection = sqlite3.connect(data_base)
        cursor = connection.cursor()
        load_data_qwery = f"select * from '{table}'"   # Запрос на данные из тблицы
        cursor.execute(load_data_qwery)
        data = cursor.fetchall()
        cursor.close()
        connection.close()
        return data
    except:
        return False

# Функция замены данных в БД (пока в одной ячейке)
def reload_data(data_base, table, old_data, new_data, second_old_data, column):
    # second_old_data параметр для отсечения чертежей с одинаковыми названиями(номера уникальны, названия нет)
    try:
        connection = sqlite3.connect(data_base)
        cursor = connection.cursor()
        if column == 'Расположение':
            # Запрос на из менение ссылки (если ссылка пустая NULL или None запена не работала)
            reload_data_qwery = f"UPDATE '{table}' SET [{column}] = '{new_data}' WHERE [Номер] = '{second_old_data}'"
        else:
            # Сам SQL запрос на изменение, также реализованно отслеживание номера чертежа если названия одинаковые
            reload_data_qwery = f"UPDATE '{table}' SET [{column}] = '{new_data}' WHERE [{column}] = '{old_data}' AND [Номер] = '{second_old_data}'"
        cursor.execute(reload_data_qwery)    # Выполонение запроса
        cursor.close()
        connection.commit()                  # Сохранение изменений
        connection.close()
        return True
    except:
        return False

# Функция удаления строки (записи) в БД
def delete_row(data_base, table, number_draw):
    try:
        connection = sqlite3.connect(data_base)
        cursor = connection.cursor()
        # SQL запрос на удаление строки
        delete_row_qwery = f"DELETE FROM '{table}' WHERE [Номер] = '{number_draw}'"
        cursor.execute(delete_row_qwery)
        cursor.close()
        connection.commit()
        connection.close()
        return True
    except:
        return False

# Функция проверки номера чертежа на совпадение (занят в базе или свободен)
def number_draw_test(data_base, table, number):
    try:
        connection = sqlite3.connect(data_base)
        cursor = connection.cursor()
        #SQL запрос на получение номеров чертежей из активной таблицы и поиск совпадений
        qwery_draw_numbers = f"SELECT [Номер] from '{table}' WHERE [Номер] = '{number}'"
        cursor.execute(qwery_draw_numbers)
        data = cursor.fetchall()
        cursor.close()
        connection.close()
        # Проверка на совпадения False - номер присутствует True - номера нет
        if len(data) != 0:
            data.clear()  # На всякий случай очистка массива данных, их может быть очень много
            return False
        else:
            data.clear()  # На всякий случай очистка массива данных, их может быть очень много
            return True
    except:
        return None

# Функция добавления новой записи (нового чертежа) в БД
def insert_draw(data_base, table, number, name, link):
    try:
        connection = sqlite3.connect(data_base)
        cursor = connection.cursor()
        # SQL запрос на вставку новых данных в таблицу
        qwery_draw_insert = f"INSERT INTO '{table}' ([Номер],[Название],[Расположение]) VALUES ('{number}','{name}','{link}');"
        cursor.execute(qwery_draw_insert)
        cursor.close()
        connection.commit()
        connection.close()
    except:
        return False

# Функция поиска совпадений в данных полученных из таблицы по которой идёт поиск
# data_mass массив данных в которых идёт поиск, parametr - то что нужно найти
def search_in_data(data_mass, parameter):
    out = []
    # Поиск по подстроке
    for line in data_mass:
        st_line = ''
        # Склеиваем кортеж в одну строку
        for word in line:
            st_line += word
        if parameter.lower() in st_line.lower():
            out.append(line)
    return out

# Функция поиска по базе
def search_in_base(data_base, table, data):
    try:
        connection = sqlite3.connect(data_base)
        cursor = connection.cursor()
        qwery_search = f"SELECT * FROM '{table}'"
        # Разработка регистронезависимого поиска Найден новый баг нужно автоматом ставить текущую таблицу
        cursor.execute(qwery_search)
        search_data = cursor.fetchall()
        out = search_in_data(search_data,data)
        cursor.close()
        connection.close()
        return out
    except:
        return False

# Функция проверки имени пользователя и пароля
def check_enter(name, password):
    try:
        connection = sqlite3.connect('users.db')  # Подключение к БД с паролями
        cursor = connection.cursor()
        qwery = f"SELECT * FROM users WHERE [Имя] = '{name}' AND [Пароль] = '{password}'"
        cursor.execute(qwery)
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        if len(result) != 0:
            return True
        else:
            return False
    except:
        return None

# Функция внесения записей в журнал изменений
# На входе: дата, имя пользователя, объект над которым совершаются действия, само действие
def log_journal_writter(user_name, target, action):
    try:
        connection = sqlite3.connect('log.db')
        cursor = connection.cursor()
        date = datetime.now()
        # Костыль времени 16:2 -> 16:02
        if date.minute < 10:
            minute = '0' + str(date.minute)
        else:
            minute = date.minute
        date_write = "{}.{}.{} {}.{}".format(date.day, date.month, date.year, date.hour, minute) # Формирование даты
        log_qwery = f"INSERT INTO log_journal ([Дата],[Пользователь],[Объект],[Действие]) VALUES ('{date_write}','{user_name}','{target}','{action}');"
        cursor.execute(log_qwery)
        cursor.close()
        connection.commit()
        connection.close()
        return True
    except:
        return False

# Функция записи и чтения пути к программе для открытия PDF
def memory_link_function(state, link=''):
    try:
        connection = sqlite3.connect('system.db')
        cursor = connection.cursor()
        # Выбор действия чтения или запись
        if state == 'write':
            qwery = f"UPDATE system SET value = '{link}' WHERE varibal = 'patch_to_pdf'"
        elif state == 'read':
            qwery = f"SELECT value FROM system WHERE varibal = 'patch_to_pdf'"
        cursor.execute(qwery)
        link_to_pdf = cursor.fetchall()
        cursor.close()
        connection.commit()
        connection.close()
        return link_to_pdf
    except:
        return False