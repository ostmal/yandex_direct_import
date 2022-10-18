from src_many_reports.different_procedures import *

import json

def print_parameters_report(parameter_name_list, global_fields_dic, report_param_dic):
    """
    Печать параметров report
    Применяется вначале и в конце взаимодействия с пользователем
    """
    print(f"Аккаунт: {report_param_dic['account']}")
    print(f"ReportType: {report_param_dic['ReportType']}")
    # Записываем предыдущие значения в текущий запрос и распечатываем
    for el in parameter_name_list:
        if el == 'FieldNames':   # Отдельный вывод для этого поля, чтобы разделить ТИПЫ ПОЛЕЙ
            print(f"{el} в разбивке по типу (сегменты, атрибуты, метрики):")
            current_full_FieldsNames_report_set = set( [ x.strip(' ') for x in   report_param_dic[el].split(",")] )
            for type_field in ['сегмент', 'атрибут', 'метрика']:
                try:
                    tmp = get_fields_list(global_fields_dic, report_param_dic['ReportType'], type_field=type_field,
                                    set_to_check=current_full_FieldsNames_report_set)
                    tmp = list(tmp)
                    tmp.sort()
                    tmp = ", ".join(tmp)
                except:
                    tmp = None
                print(f"* поля типа '{type_field}': ", tmp)
        else:
            try:
                tmp = report_param_dic[el]
            except:
                tmp = None
            print(f"{el}: {tmp}")

def get_input_data(agree):
    """
    Получаем от пользователя дату в правильном формате

    Если пользователь вводит:
    0 - выход из программы
    [enter] - выход с False
    Функуия реализована, чтобы реализовать break  из двух циклов
    """
    flag = False
    while flag == False:
        tmp = input(f"'Введите дату в формате YYYY-MM-DD (0 - выход из программы{agree}): ")

        # enter - согласиться с прошлым значением
        if not tmp and agree != '':
            return False

        if tmp == '0':
            exit_programm()

        flag = validate_date(tmp)
    return tmp


def print_goals_list(all_goals_dic):
    """
    Вывод на экран списка целей (Goals) из словаря, который получен из таблицы с аккаунтами Яндекс -Директ
    :param all_goals_dic:
    :return: all_goals_dic_dic - словарь: Порядковый номер цели - Номер цели - Описание
    """
    tmp = all_goals_dic
    tmp = tmp.replace("'", '"')
    all_goals_dic = json.loads(f"{tmp}")
    # Создадим новый словарь для вывода и выбора значений
    all_goals_dic_dic = {}
    n = 0
    for k, v in all_goals_dic.items():
        n += 1
        all_goals_dic_dic[n] = [k, v]   # значение нового словаря - список: пара НОМЕР ЦЕЛИ - ОПИСАНИЕ ЦЕЛИ

    for k ,v in all_goals_dic_dic.items():
        print(f"{k:2d} {v[0]:11s} - {v[1]}")

    return all_goals_dic_dic