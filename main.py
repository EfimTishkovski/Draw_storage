from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow, QApplication, QAction, \
    QFileDialog, QInputDialog, QMessageBox, QWidget, QCheckBox
from PyQt5.QtCore import QSize, pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from PyQt5 import QtWidgets
from PyQt5 import QtCore
import sys
import subprocess
import os
from back import *

"""
написать меню, хелп, о программе
добавить настройки при начале работы типа указать программу для открытия PDF
Написать форму для просмотра журнала изменений
"""

gl_base = ''  # Глобальная переменная для имени активной базы
gl_table = '' # Глобальная переменная для имени активной таблицы

# Глобальная функция окошка с предупреждением (уж что-то очень много их получилось)
def message_window(messege, title='Внимание!'):
    message_box = QMessageBox()
    message_box.setText(messege)
    message_box.setWindowTitle(title)
    message_box.setIcon(QMessageBox.Warning)
    message_box.setWindowIcon(QIcon('закладка-лента.png'))
    message_box.exec_()

# Глобальная функция вызова окна ошибки
def error_window(messege, title='Ошибка!'):
    message_box = QMessageBox()
    message_box.setText(messege)
    message_box.setWindowTitle(title)
    message_box.setIcon(QMessageBox.Warning)
    message_box.setWindowIcon(QIcon('ошибка.png'))
    message_box.exec_()



class Main_window(QMainWindow):

    # Подключение действий в основной класс
    def _connectAction(self):
        self.openAction.triggered.connect(self.openfile)
    # Действие
    def _createActions(self):
        self.openAction = QAction('Открыть', self)

    # Функция отображения выбранной таблицы в основном табличном виджете
    # Выбранная таблица не должна быть пустой, нужна хотя бы одна запись! (Может потом сделаю отлов этого бага)
    def info_table_show(self):
        try:
            enable_table = self.table_list.currentText()                    # Получение имени выбранной таблицы
            global gl_table
            gl_table = enable_table                                         # Передача имени активной базы в Глобальную переменную
            header_columns = names_columns(gl_base, gl_table)               # Получение заголовков
            self.Main_Table.setColumnCount(len(header_columns))             # Устанавливаем количество столбцов
            self.Main_Table.setHorizontalHeaderLabels(header_columns)       # Выводим имена заголовков в таблицу
            data = load_data(gl_base, gl_table)                             # Получение массива данных из таблицы, каждая строка - кортеж
            self.Main_Table.setRowCount(len(data))                          # Установка количества строк
            # Передача данных в таблицу
            for row in range(len(data)):
                for column in range(len(data[row])):
                    self.Main_Table.setItem(row, column, QtWidgets.QTableWidgetItem(str(data[row][column])))
            self.Main_Table.resizeColumnsToContents()                           # Подгонка размеров колонок по содержимому
        except:
            self.statusBar().showMessage('Ошибка отображения таблицы')

    # Функция обработки открытия файла, получения и отображения данных
    def openfile(self):
        try:
            basename = QFileDialog.getOpenFileName(self, 'Открыть файл', '', '*.db')[0]  # Получение от пользователя имени базы для открытия
            if basename:
                #self.activ_base_name = basename
                global gl_base
                gl_base = basename      # Передача имени аткивной базы в глобальную переменную, можно использовать в любом классе

                out_list_tablename = []                            # Массив для имён таблиц
                base_tables = names_tables(gl_base)                # Получение имён таблиц из базы
                for table in base_tables[0]:                       # Формирование массива с именами таблиц
                    out_list_tablename.append(table[0])

                self.table_list.addItems(out_list_tablename)       # Добавление имён таблиц в выпадающий список
                self.info_table_show()                             # Отбражение содержимого первой таблицы
              
                self.statusBar().showMessage(f'Подключена база: {basename}.')
                self.line_base_name.setText(basename)         # Вывод пути и имени базы в окошке "Используемая база"
        except:
            self.statusBar().showMessage('Ошибка подключения')

    # Функция открывающая чертёж
    def show_drawing(self, item):
        try:
            # Получение ссылки расположения чертежа из таблички (Main_Table)
            if item.column() == 2 and self.change_flag is False:
                item.setFlags(QtCore.Qt.ItemIsEnabled)    # Запрет на редактирование при нажатии
                path = item.text()
                # Путь к программе открывабщей pdf-файлы
                path_to_acrobat = os.path.abspath('C:\Program Files (x86)\Foxit Software\Foxit PhantomPDF\FoxitPhantomPDF.exe')

                # Открытие документа, все страницы
                process = subprocess.Popen([path_to_acrobat, '/A', 'page = ALL', path], shell=False,stdout=subprocess.PIPE)
                process.wait()

            elif item.column() <= 1 and self.change_flag is False:
                item.setFlags(QtCore.Qt.ItemIsEnabled)    # Запрет на редактирование при нажатии других ячеек

            # Запрет на изменение номера чертежа и номера записи в режиме редактирования
            elif item.column() == 0 and self.change_flag is True:
                item.setFlags(QtCore.Qt.ItemIsEnabled)
                # дописать функцию, с окошком сообщения, что редактирование не возможно

            elif item.column() == 2 and self.change_flag is True:
                # Замена ссылки на чертёж
                run = self.new_link_draw(item)
                if run:
                    self.statusBar().showMessage('Чертёж успешно заменён')

            elif item.column() == 1 and self.change_flag is True:
                # Замена названия чертежа
                second_item = self.Main_Table.item(item.row(), item.column() - 1)
                self.new_item_cell(item.row(), item.column(), item.text(), second_item.text())
        except:
            self.statusBar().showMessage('Ошибка открытия чертежа')

    # Функция получения новой ссылки на чертёж
    def new_link_draw(self, item):
        try:
            link = QFileDialog.getOpenFileName(self, 'Новый чертёж', '', '*.pdf')[0]  # Получение новой ссылки
            old_link = item.text()                                                    # Старая ссылка
            name_column = self.Main_Table.horizontalHeaderItem(item.column()) # Получение имени столбца
            second_item = self.Main_Table.item(item.row(), 0)  # Получение номера чертежа (если ссылки вдруг одинаковые)
            self.Main_Table.setItem(item.row(), item.column(),
                                QtWidgets.QTableWidgetItem(str(link)))  # Установка новой ссылки в выбранную ячейку
            # Замена ссылки, работает таже функция, что и для замены названия чертежа
            reload_data(gl_base, gl_table, old_link, link, second_item.text(), name_column.text())
            log_journal_writter(self.activ_user, second_item.text(), 'Замена чертежа') # Запись в журнал
            return True
        except sqlite3.Error as error:
            self.statusBar().showMessage('Ошибка замены чертежа', error)

    # Функция замены названия чертежа (детали) в базе
    def new_item_cell(self, row, column, old_data, second_old_data):
        # second_old_data номер чертежа у которого меняется название
        try:
            text, ok = QInputDialog.getText(self, 'Замена названия чертежа', 'Введите новое имя:')

            if ok:
                self.Main_Table.setItem(row, column, QtWidgets.QTableWidgetItem(text))   # Установка нового значения в выбранную ячейку
                name_column = self.Main_Table.horizontalHeaderItem(row + 1)              # Получение имени столбца
                reload_data(gl_base, gl_table, old_data, text, second_old_data, name_column.text())  # Замена значения а БД
                log_journal_writter(self.activ_user, second_old_data, 'Изменение названия')   # Запись в журнал изменений
                self.statusBar().showMessage('Название детали заменено')
        except:
            self.statusBar().showMessage('Ошибка замены названия детали')

    # Функция смены режимов редактирования и просмотра
    def change_button_pessed(self):
        self.change_flag = not self.change_flag   # Инверсия логического значения флага при нажатии
        if self.change_flag:
            self.change_signal_label.setText('Вход выполнен: режим редактирования ативен')
        else:
            self.change_signal_label.setText('Вход не выпонен: режим просмотра')

    # Функция принятия номера выделонной строки (решение странное)
    def select_row_number(self, row):
        self.selected_row = row

    # Функция удаления строки (удаление детали из базы)
    def delete_row(self):
        try:
            if self.change_flag and self.selected_row > 0:
                # Вызов окошка одтверждения действия
                reply = QMessageBox.question(self, 'Подтверждение', 'Удалить строку?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                # Если ответ 'YES' то функция продолжает работу
                if reply == QMessageBox.Yes:
                    row = self.selected_row         # Получение номера строки из глобальной переменной
                    number_draw = self.Main_Table.item(row, 0).text() # Получение номера чертежа для поиска строки в БД
                    self.Main_Table.removeRow(row)
                    run = delete_row(gl_base, gl_table, number_draw)  # Само удаление строки, run получает True или False
                    if run:
                        log_journal_writter(self.activ_user, number_draw, 'Чертёж удалён')  # Запись в журнал об удалении
                        self.statusBar().showMessage('Строка удалена')
                    else:
                        self.statusBar().showMessage('Ошибка удаления строки: не отработала функция')
                    self.selected_row = -1
                else:
                    self.statusBar().showMessage('Отмена удаления строки')
            elif self.change_flag and self.selected_row < 0:
                # Окошко предупреждения о не выделенной строке
                message_window('Строка не выбрана!')

        except:
            self.statusBar().showMessage('Ошибка удаления строки: Исключение')

    # Функция вызова окна добавления новой записи
    def insert_data(self):
        try:
            # Условие активации кнопки "Добавить строку": включен режим редактирования, подключена база и выбрана таблица
            if self.change_flag and gl_base != '' and gl_table != '':
                self.change_win.show()    # Показать окно
            elif self.change_flag and gl_base == '':
                # Окошко предупреждения о не подключеной базе
                message_window('Подключите базу')
            elif self.change_flag and gl_base != '' and gl_table == '':
                # Окошко предупреждения о не выбранной таблице
                message_window('Подключите таблицу')
        except:
            self.statusBar().showMessage('Ошибка добавления записи')

    # Функция добавления новой строки в базу
    def new_data_row(self, number, name, link):
        try:
            insert_draw(gl_base, gl_table,number, name, link)
            self.info_table_show()   # Обновление таблицы в главном окне (по факту отрисовка её заново)
            log_journal_writter(self.activ_user, number, 'Добавлена новая деталь')  # Запись в журнал изменений
            self.statusBar().showMessage('Данные успешно добавлены')
        except:
            self.statusBar().showMessage('Ошибка добавления данных')

    # Функция для вызова окна поиска
    def search_window(self):
        self.search_win.show()

    # Функция входа в аккаунт
    def enter(self):
        fild_flag = False # Флаг для обработки условия не пустых полей
        # Можно и без него, но нехотелось городить множественные вложенные условия
        # Проверка на пустые поля ввода
        user_name = self.username_lineEdit.text()
        password = self.password_lineEdit.text()
        if user_name !='' and password != '':
            fild_flag = True
        elif user_name == '' or password == '':
            fild_flag = False
        else:
            fild_flag = False

        # Проверка на уже выполненый вход и заполненые поля ввода
        if self.change_flag is False and fild_flag:
            enter_flag = check_enter(user_name, password)
            # Действия после проверки имени и пароля
            if enter_flag:
                self.change_flag = True
                self.change_signal_label.setText('Вход выполнен: режим редактирования ативен')
                self.change_signal_label_2.setText('Пользователь: ' + user_name)
                self.delete_button.setEnabled(True)  # Активация кнопки "удалить строку"
                self.append_button.setEnabled(True)  # Активация кнопки "добавить строку"
                self.activ_user = user_name          # Присвоение имени пользователя
            elif enter_flag is False:
                message_window('Неверное имя пользователя или пароль', ' Вход не выполнен')
            elif enter_flag is None:
                error_window('Ошибка входа')
        elif self.change_flag:
            message_window('Вход уже выполнен!', 'Сообщение')
        elif fild_flag is False:
            message_window('Неверное имя пользователя или пароль', 'Ошибка входа')

    # Функция выхода из аккаунта
    def exit_account(self):
        reply = QMessageBox.question(self, 'Подтверждение', 'Выйти из аккаунта?', QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        # Если ответ 'YES' то выполняется выход
        # Если ответ 'NO' то ничего не происходит пользователь дальше активен
        if reply == QMessageBox.Yes:
            self.delete_button.setEnabled(False)  # Кнопка "удалить строку" по умолчанию не активна"
            self.append_button.setEnabled(False)  # Кнопка "добавить строку" по умолчанию не активна"
            self.change_flag = False
            self.password_lineEdit.clear()  # Очистка полей посде выхода
            self.username_lineEdit.clear()
            self.change_signal_label.setText('Вход не выполнен: режим просмотра')
            self.statusBar().showMessage('Выход из аккауна выполнен')
            self.activ_user = ''  # Сброс имени пользователя

    # Функция работы Кнопки показать пароль
    def show_password(self):
        mode = self.password_lineEdit.echoMode()   # От тут меня прёт разница в e и E, капец не очевидно в документации, 20 минут искал и случайно догадался, а так да, работает
        if mode == 0:
            self.password_lineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        elif mode == 2:
            self.password_lineEdit.setEchoMode(QtWidgets.QLineEdit.Normal)


    # Основная функция приложения
    def __init__(self):
        super(Main_window, self).__init__()
        loadUi('simple_design.ui', self)
        # Дочерние окна
        self.change_win = Change_form()    # Создание экземпляра класса Change_form
        self.change_win.setWindowIcon(QIcon('галочка.png'))  # Установка значка для окна добавления чертежа

        self.search_win = Search_form()    # Создание экземпляра класса Search_form
        self.search_win.setWindowIcon(QIcon('фонарик.png'))  # Установка значка для окна поиска

        # Инциализация (состояние некоторых кнопок на момент запуска приложения)
        self.delete_button.setEnabled(False)  # Кнопка "удалить строку" по умолчанию не активна"
        self.append_button.setEnabled(False)  # Кнопка "добавить строку" по умолчанию не активна"

        # Програмная вставка иконок в кнопки (эксперимент)
        self.delete_button.setIcon(QIcon('удалить-64.png'))
        self.delete_button.setIconSize(QSize(35, 35))
        self.append_button.setIcon(QIcon('загрузка-обновлений.png'))
        self.append_button.setIconSize(QSize(35, 35))
        self.search_button.setIcon(QIcon('поиск.png'))
        self.search_button.setIconSize(QSize(35, 35))

        # Переменные
        self.change_flag = False          # Переменная состояния флага редактирования по умолчанию режим просмотра
        self.table_names = []             # Массив для имён таблиц
        self.selected_row = -1            # Переменная номер выделенной строки
        self.activ_user = ''              # Имя активного пользователя

        # Обработка событий и сигналов
        self._createActions()  # Подключение дествий в основной функции
        self._connectAction()  # Подключение действий при нажатии пунктов меню к основной функции
        self.connect_base_button.clicked.connect(self.openfile)       # Обработчик кнопки "Подключить базу"
        self.table_list.activated[str].connect(self.info_table_show)  # Обработчик смены таблицы в выпадающем списке
        self.Main_Table.itemClicked.connect(self.show_drawing)        # Обработчик клика на ячейку, показывает чертёж
        #self.change_button.clicked.connect(self.change_button_pessed) # Обработчик кнопки "Внести изменения"
        self.Main_Table.verticalHeader().sectionClicked.connect(self.select_row_number)  # Обработчик события нажатия на заголовок строки, возвращает номер выделенной строки
        self.delete_button.clicked.connect(self.delete_row)            # Обработчик кнопки "Удалить строку"
        self.append_button.clicked.connect(self.insert_data)           # Обработчик кнопки "Добавить строку"
        self.change_win.data[str, str, str].connect(self.new_data_row) # Обработчик события передачи и вставки новой строки
        self.search_button.clicked.connect(self.search_window)         # Обработчик кнопки вызова окна поиска
        self.input_button.clicked.connect(self.enter)                  # Обработчик кнопки "Войти"
        self.password_lineEdit.setEchoMode(QtWidgets.QLineEdit.Password)  # По умолчанию ключ скрыт
        self.show_password_button.clicked.connect(self.show_password)     # Обработчик кнопки показать пароль
        self.exit_account_button.clicked.connect(self.exit_account)       # Обработчик кнопки "Выход из учётной записи"

# Создание окна для внесения новых записей в БД
class Change_form(QWidget):
    data = pyqtSignal(str, str, str)  # Создание объекта сигнал, для передачи 3-х значений между окнами

    def __init__(self):
        super(Change_form, self).__init__()
        loadUi('change_form.ui', self)
        self.buttonBox.clicked.connect(self.button_click)     # Обработчик нажатия Ok/Cancel
        self.file_button.clicked.connect(self.link_new_file)  # Обработчик нажатия на кнопку обзор

    # Функция обработки событий и получения информации из окна вводна данных
    def button_click(self, button):
        pressed_button = self.buttonBox.standardButton(button)   # Обработка нажптия на кнопку (любую ok или cancel)
        # Распознавание какая именно кнопка нажата и отработка действий
        if pressed_button == QtWidgets.QDialogButtonBox.Ok:
            self.messege_label.setText('')
            # Проверка на пустой ввод
            number = self.number_lineEdit.text()
            name = self.name_lineEdit.text()
            link = self.location_lineEdit.text()
            # Условие проверки на заполнение всех полей
            if all([number, name, link]):
                enter_flag = True
            else:
                enter_flag = False

            # Проверка на наличие номера в базе
            if number_draw_test(gl_base, gl_table, self.number_lineEdit.text()) and enter_flag:
                # Отправка сигнала с данными в основное окно
                self.data.emit(self.number_lineEdit.text(), self.name_lineEdit.text(), self.location_lineEdit.text())
                self.number_lineEdit.clear()  # Очистка поля для ввода после считывания
                self.name_lineEdit.clear()
                self.location_lineEdit.clear()
                self.close()  # Закрытие окна
            elif enter_flag is False:
                # Окошко предупреждения о пустом вводе
                message_window('Поля ввода не могут быть пустыми')
            else:
                self.messege_label.setText('Номер уже есть в базе')

        elif pressed_button == QtWidgets.QDialogButtonBox.Cancel:
            self.number_lineEdit.clear()  # Очистка поля для ввода после считывания
            self.name_lineEdit.clear()
            self.location_lineEdit.clear()
            self.messege_label.setText('')
            self.close()

    # Функция вставки ссылки на файл
    def link_new_file(self):
        link = QFileDialog.getOpenFileName(self, 'Чертёж', '', '*.pdf')[0]  # Получение новой ссылки
        self.location_lineEdit.setText(link)

# Создание окна формы поиска
class Search_form(QWidget):
    def __init__(self):
        super(Search_form, self).__init__()
        loadUi('search_form.ui', self)
        self.base_Button.clicked.connect(self.base)  # Обработчик кнопки "Обзор"
        self.activ_base_checkBox.stateChanged.connect(self.choise_base_sourse)     # Обработчик состояния чекбокса "Использовать активную базу"
        self.search_Button.clicked.connect(self.search)                            # Обработчик кнопки "Найти"

    # Функция добавления базы в ручную
    def base(self):
        base = QFileDialog.getOpenFileName(self, 'Выбор базы данных', '', '*.db')[0]  # Получение новой ссылки
        self.base_name_lineEdit.clear()                    # Очистка окна с именем базы (при смене БД)
        self.base_name_lineEdit.setText(base)              # Установка нового имени базы
        # Этот кусок кода добавляет имена таблиц в комбобокс после выбора базы в ручную
        out_list_tablename = []  # Массив для имён таблиц
        base_tables = names_tables(self.base_name_lineEdit.text())  # Получение имён таблиц из базы
        # Формирование массива с именами таблиц
        for table in base_tables[0]:
            out_list_tablename.append(table[0])
        self.table_name_comboBox.clear()
        self.table_name_comboBox.addItems(out_list_tablename)  # Добавление имён таблиц в выпадающий список

    # Функция обработки чекбокса выбора БД
    def choise_base_sourse(self, state):
        if state == Qt.Checked:
            # Если галка стоит, то подключается база из глобальной переменной
            self.base_Button.setEnabled(False)
            self.base_name_lineEdit.clear()
            self.base_name_lineEdit.setText(gl_base)
        else:
            # Если галки нет, кнопка обзор активна и база задаётся в ручную
            self.base_Button.setEnabled(True)

        # После получения имени базы, закидываем имена таблиц в комбобокс
        out_list_tablename = []                                     # Массив для имён таблиц
        base_tables = names_tables(self.base_name_lineEdit.text())  # Получение имён таблиц из базы
        # Формирование массива с именами таблиц
        for table in base_tables[0]:
            out_list_tablename.append(table[0])
        self.table_name_comboBox.clear()
        self.table_name_comboBox.addItems(out_list_tablename)       # Добавление имён таблиц в выпадающий список

    # Сама функция поиска
    def search(self):
        # Считывание имени базы и таблицы, через переменные нагляднее
        base = self.base_name_lineEdit.text()
        table = self.table_name_comboBox.currentText()
        if base != '' and table != '':
            qwery_data = self.input_lineEdit.text()
            out_data = search_in_base(base, table, qwery_data)
            if len(out_data) == 0:
                # Окошко ничего не найдено
                message_window('Ничего не найдено')
            else:
                # Вывод результатов поиска в окно
                for line in out_data:
                    out = ''
                    for element in line:
                        out += element + '   '
                    out += '\n'            # Немножко магии чтобы выводились все строки
                    self.output_textEdit.insertPlainText(out)
        else:
            # Окошко предупреждения о не выбранной таблице и/или базе
            message_window('Невыбрана база или таблица')

# Запуск приложения
if __name__ == '__main__':
    app = QApplication(sys.argv)                   # Новый объет приложения экземпляр класса Qtapplication, sys.arg - список аргументов ком. строки
    window = Main_window()                         # Создание экземпляра класса Main_window
    window.setWindowIcon(QIcon('virtualbox.png'))  # Установка значка приложения
    window.show()                                  # Показать окно на экране
    sys.exit(app.exec_())                          # Запуск основного цикла приложения sys.exit() гарантирует чистый выход
