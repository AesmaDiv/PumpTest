"""
    Модуль журналирования
    logged - декоратор журналирования метода
    log - метод записи сообщения в журнал
"""
from datetime import date


class Journal:
    """ Класс журналирования """
    IS_NUMERATED = True     # вкл/выкл нумерации строк
    WRITE_TO_FILE = False   # вкл/выкл записи в файл
    LINE_NUMBER = 0         # текущий номер строки

    @staticmethod
    def logged(func):
        """ Декоратор журналирования """
        def wrapped(*args, **kwargs):
            Journal.log(f"{func.__module__}::\t{func.__doc__}")
            result = func(*args, **kwargs)
            return result
        return wrapped

    @staticmethod
    def logged_msg(begin_message = '', end_message = ''):
        """ Декоратор журналирования """
        def wrapped(func):
            def wrap(*args, **kwargs):
                if begin_message != '':
                    Journal.log(func.__name__, '\t', begin_message)
                result = func(*args, **kwargs)
                if end_message != '':
                    Journal.log(func.__name__, '\t', end_message)
                return result
            return wrap
        return wrapped

    @staticmethod
    def log(*messages, end='\n'):
        """ Запись сообщения в журнал """
        message = " ".join([str(item) for item in messages])
        if Journal.IS_NUMERATED:
            Journal.LINE_NUMBER += 1
            message = str(Journal.LINE_NUMBER) + '> ' + message
        cur_date = date.today().strftime('%Y-%m-%d')
        if Journal.WRITE_TO_FILE:
            try:
                file_ = open(cur_date, 'a')
                file_.write(message + '\n')
                # file_.writelines([(message)])
                file_.close()
            except IOError as error:
                print("Log file error: %s" % error)
        print(message, end=end)
