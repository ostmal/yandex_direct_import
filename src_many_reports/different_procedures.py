from src_many_reports.create_dic import *

import datetime
import sys
import logging

def validate_date(date_text):
    """
    Проверка правильного формата даты
    """
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        print("Некорректный формат даты, правильно: YYYY-MM-DD")
        return False

def exit_programm():
    """
    Выход из программы с выводом сообщения на печать
    """
    print("\n*** Выход из программы ***")
    sys.exit()




