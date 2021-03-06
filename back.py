import sqlite3

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
    except sqlite3.Error as error:
        print('Ошибка при подключении к базе', data_base, error)

# Функция получения имён столбцов в таблице базы
def names_columns(data_base, table):
    try:
        connection = sqlite3.connect(data_base)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute('select * from {}'.format(table))
        line = cursor.fetchone()
        names_column = line.keys()
        cursor.close()
        connection.close()
        return names_column
    except sqlite3.Error as error:
        print('Ошибка при подключении к базе', data_base, error)

# Функция получения информации из базы
def load_data(data_base, table):
    try:
        connection = sqlite3.connect(data_base)
        cursor = connection.cursor()
        load_data_qwery = 'select * from {}'.format(table)   # Запрос на данные из тблицы
        cursor.execute(load_data_qwery)
        data = cursor.fetchall()
        cursor.close()
        connection.close()
        return data
    except sqlite3.Error as error:
        print('Ошибка при загрузке данных из таблицы', table, error)

# Функция замены данных в БД (пока в одной ячейке)
def reload_data(data_base, table, old_data, new_data, second_old_data, column):
    # second_old_data параметр для отсечения чертежей с одинаковыми названиями(номера уникальны, названия нет)
    try:
        connection = sqlite3.connect(data_base)
        cursor = connection.cursor()
        # Сам SQL запрос на изменение, также реализованно отслеживание номера чертежа если названия одинаковые
        reload_data_qwery = f"UPDATE {table} SET [{column}] = '{new_data}' WHERE [{column}] = '{old_data}' AND [Номер] = '{second_old_data}'"
        cursor.execute(reload_data_qwery)    # Выполонение запроса
        cursor.close()
        connection.commit()                  # Сохранение изменений
        connection.close()
        return True
    except sqlite3.Error as error:
        print('Ошибка при записи данных', table, error) # Возможно сообщение лишнее, показать в приложении не получится
        return False

# Функция удаления строки (записи) в БД
def delete_row(data_base, table, number_draw):
    try:
        connection = sqlite3.connect(data_base)
        cursor = connection.cursor()
        # SQL запрос на удаление строки
        delete_row_qwery = f"DELETE FROM {table} WHERE [Номер] = '{number_draw}'"
        cursor.execute(delete_row_qwery)
        cursor.close()
        connection.commit()
        connection.close()
        return True
    except sqlite3.Error as error:
        print('Ошибка удаления строки', table, error)
        return False

# Функция проверки номера чертежа на совпадение (занят в базе или свободен)
def number_draw_test(data_base, table, number):
    try:
        connection = sqlite3.connect(data_base)
        cursor = connection.cursor()
        #SQL запрос на получение номеров чертежей из активной таблицы и поиск совпадений
        qwery_draw_numbers = f"SELECT [Номер] from {table} WHERE [Номер] = '{number}'"
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

    except sqlite3.Error as error:
        print('Ошибка поиска', error)

# Функция добавления новой записи (нового чертежа) в БД
def insert_draw(data_base, table, number, name, link):
    try:
        connection = sqlite3.connect(data_base)
        cursor = connection.cursor()
        # SQL запрос на вставку новых данных в таблицу
        qwery_draw_insert = f"INSERT INTO {table} ([Номер],[Название],[Расположение]) VALUES ('{number}','{name}','{link}');"
        cursor.execute(qwery_draw_insert)
        cursor.close()
        connection.commit()
        connection.close()
    except sqlite3.Error as error:
        print('Ошибка добавления записи',error)

# Функция поиска по базе
def search_in_base(data_base, table, data):
    try:
        connection = sqlite3.connect(data_base)
        cursor = connection.cursor()
        # Анализ ввода, по результату выбирается столбец
        if data.isalpha():
            column = 'Название'
        elif data[-4:] == '.pdf':
            column = 'Расположение'
        else:
            column = 'Номер'
        qwery_search = f"SELECT * FROM {table} WHERE [{column}] = '{data}'"
        cursor.execute(qwery_search)
        search_data = cursor.fetchall()
        cursor.close()
        connection.commit()
        connection.close()
        return search_data
    except sqlite3.Error as error:
        print('Ошибка поиска', error)

# Функция проверки имени пользователя и пароля
def check_enter(name, password):
    try:
        connection = sqlite3.connect('users.db')  # Подключение к БД с паролями
        cursor = connection.cursor()
        qwery = f"SELECT * FROM users WHERE [Имя] = '{name}' AND [Пароль] = '{password}'"
        cursor.execute(qwery)
        result = cursor.fetchall()
        if len(result) != 0:
            return True
        else:
            return False
    except:
        return None
