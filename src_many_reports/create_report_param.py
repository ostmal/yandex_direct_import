from src_many_reports.operations_with_database import *
from src.add_to_table_YD import *
from src_many_reports.code_optimization import *

import pandas as pd
import datetime
import json


def create_report_param(credential_bd):
    """
    В диалоге с пользователем - формирование параметров запроса
    :return: Словарь - параметры запроса
    """
    report_param_dic = {}
    global_fields_dic = create_fields_dic()
    parameter_name_list = ['DateRangeType', 'DateFrom', 'DateTo', 'FieldNames', 'Filters', 'Goals', 'AttributionModels']

    # ***
    # *** ШАГ 1 - Считываю список аккаунтов **********************************************
    sql = f"SELECT account_id, organization_name, account, token, goals FROM {credential_bd['schema']}.accounts;"
    df_accounts = read_from_db(credential_bd, sql)
    # Переименуем столбцы
    df_accounts = df_accounts.rename(columns={'account_id': 'id'})
    df_accounts['id'] = df_accounts['id'].astype(int)
    df_accounts = df_accounts.set_index('id')

    while True:
        print("\n","*** ШАГ 1: Выбрать аккаунт ***")
        print(df_accounts[['organization_name', 'account']])

        id_str = input("Введите чиcло - номер аккаунта (0 - выход из программы):")
        if id_str == '0':
            exit_programm()

        try:
            id = int(id_str)
            # Проверяем - такой аккаунт есть?
            df_accounts.loc[id]
            # Сохраним параметры аккаунта (id + аккаунт + токен)
            report_param_dic['account_id'] = id
            report_param_dic['account'] = df_accounts.loc[id, 'account']
            report_param_dic['token'] = df_accounts.loc[id, 'token']
            report_param_dic['all_goals_dic'] = f"{df_accounts.loc[id, 'goals']}"   # Словарь всех целей (строка)
            break
        except:
            print("\nВы ошиблись, такого аккаунта нет!")
            continue


    # ***
    # *** ШАГ 2 - Выбор ТИПА report **********************************************
    report_dic = get_dictionary('report_dic')
    while True:
        print("\n","*** ШАГ 2: Выбрать тип отчета ***")
        for el in report_dic:
            print(el, report_dic[el])

        id_str = input("Введите чиcло - номер отчета (0 - выход из программы):")
        if id_str == '0':
            exit_programm()

        try:
            id = int(id_str)
            # Проверяем - такой аккаунт есть? Сохраним номер и название report
            report_param_dic['ReportType'] = report_dic[id]
            report_param_dic['Report_id'] = id

            break
        except:
            print("\nВы ошиблись, такого типа отчета нет!")
            continue


    # ***
    # *** Считываю параметры последнего запроса по выбраннуму отчету **********************************
    sql = f"""
                select * from {credential_bd['schema']}.parameters_report
                where account_id = {report_param_dic['account_id']} and report_id = {report_param_dic['Report_id']} and log_datetime is not NULL
                order by log_datetime desc 
                limit 1;
            """
    df_last_parameters_report = read_from_db(credential_bd, sql)
    # Проверяем: df-пустой?
    if df_last_parameters_report.empty:
        print(f"\nПо этому аккаунту еще не выполнялись запросы типа {report_param_dic['ReportType']}!")
    else:
        print(f"\n{df_last_parameters_report.loc[0,'log_datetime']} - последнее дата-время выполнения такого запроса")
        print("\n*** Параметры последнего запроса:")

        # Записываем предыдущие значения в текущий запрос
        for el in parameter_name_list:
            report_param_dic[el] = df_last_parameters_report.loc[0, el.lower()]
        # Rаспечатываем
        print_parameters_report(parameter_name_list, global_fields_dic, report_param_dic)


    input("\n[enter] - продолжить...")


    # ***
    # *** ШАГ 3 - Выбор DateRangeType **********************************************
    DateRangeType_dic = get_dictionary('DateRangeType_dic')
    while True:
        print("\n","*** ШАГ 3: Выбрать DateRangeType - тип временного диапазона ***")
        for el in DateRangeType_dic:
            print(f"{el:2d}", DateRangeType_dic[el])

        try:
            print(f"\n{report_param_dic['DateRangeType']} - текущее значение этого параметра")
            agree = ', [enter] - согласиться с текущим значением'
        except:
            agree = ''

        id_str = input(f"Введите чиcло (0 - выход из программы{agree}):")

        # enter - согласиться с текущим значением
        if id_str == "" and agree != '':
            break

        if id_str == '0':
            exit_programm()

        try:
            id = int(id_str)
            # Проверяем - есть такое значение DateRangeType + сохраним
            report_param_dic['DateRangeType'] = DateRangeType_dic[id]
            break
        except:
            print("\nВы ошиблись, такого значения DateRangeType нет!")
            continue


    # ***
    # *** ШАГ 3_1 + 3_2 - Выбор [ DateFrom - DateTo ] *******************************************
    if report_param_dic['DateRangeType'] == 'CUSTOM_DATE':
        print("\n","*** ШАГ 3_1: Задать DateFrom - начало временного диапазона ***")
        try:
            print(f"\n{report_param_dic['DateFrom']} - текущее значение этого параметра")
            agree = ', [enter] - согласиться с текущим значением'
        except:
            agree = ""

        tmp = get_input_data(agree)
        if tmp:
            report_param_dic['DateFrom'] = tmp


        print("\n","*** ШАГ 3_2: Задать DateTo - конец временного диапазона ***")
        try:
            print(f"\n{report_param_dic['DateTo']} - текущее значение этого параметра")
            agree = ', [enter] - согласиться с текущим значением'
        except:
            agree = ""

        tmp = get_input_data(agree)
        if tmp:
            report_param_dic['DateTo'] = tmp
    else: # тогда необходимо затереть DateFrom - DateTo
        report_param_dic['DateFrom'] = None
        report_param_dic['DateTo'] = None


    # ***
    # *** ШАГ 4 - Выбор FieldNames **********************************************

    print("\n","*** ШАГ 4: Выбрать FieldNames - наименования полей, по которым запрашиваем статистику ***")

    num_type_field = 0
    for type_field in ['сегмент', 'атрибут', 'метрика']:
        num_type_field += 1
        while True:
            # Полный SET ВСЕХ ВОЗМОЖНЫХ полей из YD для этого report
            full_fields_YD_set = get_fields_list(global_fields_dic, report_param_dic['ReportType'], type_field=type_field)
            full_fields_YD_list = list(full_fields_YD_set)
            full_fields_YD_list.sort()
            # Если таких типов у данного report нет - дальше
            if full_fields_YD_list == []:
                break

            print(f"\n", f"*** ШАГ 4_{num_type_field}: Выбрать поля типа '{type_field.upper()}' ***")

            # Текущий SET ВСЕХ полей (всех типов) этого report
            try:
                current_full_FieldsNames_report_set = set([x.strip(' ') for x in report_param_dic['FieldNames'].split(",")])
            except:
                current_full_FieldsNames_report_set = set()

            # Полный SET ВСЕХ ВОЗМОЖНЫХ полей из YD для этого report (для выбора)
            n = 0
            for el in full_fields_YD_list:
                n +=1
                print(f"{n:2d}", el)

            # Текущий SET этого типа полей этого report
            current_fields_set = get_fields_list(global_fields_dic, report_param_dic['ReportType'], type_field=type_field, set_to_check=current_full_FieldsNames_report_set)
            current_fields_list = list(current_fields_set)
            current_fields_list.sort()

            # Текущий SET полей ДРУГОГО ТИПА этого report (ждя сохранения результата)
            current_fields_other_type_set = (current_full_FieldsNames_report_set - current_fields_set)

            try:
                print(f"\n{current_fields_list} - текущее значение этого параметра")
                agree = '1'
            except:
                agree = ''

            print(f"Введите через запятую числа - выбранные поля")
            print("Другие варианты:")
            if agree != '':
                print("[enter] согласиться с текущим значением")
            print("null    задать пустое значение параметра")
            if agree != '':
                print("+       добавить дополнительные поля к текущему списку")
                print("-       добавить дополнительные поля к текущему списку")
            print("all     выбрать ВСЕ поля")
            print("0       выход из программы")
            id_str = input(":")

            # enter - согласиться с текущим значением
            if id_str == "" and agree != '':
                # Проверка полей на совместимость (взаимоисключающие поля). см:
                # https://yandex.ru/dev/direct/doc/reports/compatibility.html
                # Необходимо учитывать предыдущие ТИПЫ полей
                set_to_check = current_fields_set
                if num_type_field == 2:  # На этапе "атрибут"
                    s1 = get_fields_list(global_fields_dic, report_param_dic['ReportType'], type_field="сегмент",
                                         set_to_check=current_full_FieldsNames_report_set)
                    set_to_check = set_to_check | s1
                if num_type_field == 3:  # На этапе "метрика"
                    s1 = get_fields_list(global_fields_dic, report_param_dic['ReportType'], type_field="сегмент",
                                         set_to_check=current_full_FieldsNames_report_set)
                    s2 = get_fields_list(global_fields_dic, report_param_dic['ReportType'], type_field="атрибут",
                                         set_to_check=current_full_FieldsNames_report_set)
                    set_to_check = set_to_check | s1 | s2

                result_check = fields_check(set_to_check)
                if result_check != True:  # Результат проверки - отрицательный
                    print(f"\nОШИБКА! Ограничение Яндекс_директ: {result_check}")
                    input("\n[enter] - продолжить...")
                    continue # не сохраняем - все заново

                break # не сохраняем - потому, что уже сохранено

            elif id_str == '0':
                exit_programm()

            elif id_str == 'null':
                current_fields_set = set()

            elif id_str == 'all':
                current_fields_set = full_fields_YD_set

            elif id_str in ['+', '-'] and agree != '':
                current_fields_set = selection_fields_plus_minus(id_str, current_fields_set, full_fields_YD_set)

            # Обработка введенного списка чисел
            else:
                try:
                    index_list = id_str.split(",")
                    index_list = [(int(x) - 1) for x in index_list]
                    current_fields_set = set([full_fields_YD_list[i] for i in index_list])
                except:
                    print("\nОшибка! Некорректный список чисел!")
                    continue

            # Сохраняем результат в текущем словаре
            l = list(current_fields_other_type_set | current_fields_set)
            l.sort()
            report_param_dic['FieldNames'] = ", ".join(l)


    # ***
    # *** ШАГ 5 - Задать Filters **********************************************
    while True:
        print("\n","*** ШАГ 5: Задать Filters - фильтрация ***")

        try:
            print(f"\n{report_param_dic['Filters']} - текущее значение этого параметра")
            agree = ', [enter] - согласиться с текущим значением'
        except:
            agree = ''
        print("Синтакис описан здесь: https://yandex.ru/dev/direct/doc/reports/filters.html")
        print('{"Field": "CampaignType","Operator": "EQUALS","Values": ["TEXT_CAMPAIGN"]}')
        print("Внимание! Используем двойные кавычки!")
        id_str = input(f"Введите новое значение Filters (0 - выход из программы, null - задать пустое значение параметра{agree}):")

        # enter - согласиться с текущим значением
        if id_str == "" and agree != '':
            break
        elif id_str == '0':
            exit_programm()
        elif id_str == 'null':
            report_param_dic['Filters'] = id_str
            break

        # Cохраним
        report_param_dic['Filters'] = id_str
        break

    # ***
    # *** ШАГ 6 - Задать Goals **********************************************
    while True:
        print("\n","*** ШАГ 6: Выбрать Goals - список целей ***")


        try:
            flag_all_goals_list = True   # Выведен список целей
            all_goals_dic_dic = print_goals_list(report_param_dic['all_goals_dic'])
        except:
            flag_all_goals_list = False   # Список целей не выведен

        try:
            if report_param_dic['Goals'] != None:
                d1 = json.loads(report_param_dic['Goals'].replace("'", '"'))
                d2 = {int(key):d1[key] for key in d1}
                print(f"\n{d2} - текущее значение этого параметра")
                agree = ', [enter] - согласиться с текущим значением'
            else:
                agree = ''
        except:
            agree = ''

        print("\nВсего можно задать ТРИ цели:")
        print("1:добавление в корзину,   2:переход в корзину,   3:покупка")
        if flag_all_goals_list:
            print("\nВведите через запятую пары чисел по форме:")
            print("[номер цели (1, 2 или 3)]:[порядковый номер выбранной цели из ЯндексМетрики в списке],...")
            print("Например: 1:3,2:4,3:2")
            print("Если вначале написать 'manual' - можно писать номера целей в явной форме (manual 1:782945678, 2:637894)")
            id_str = input(f"(0 - выход из программы, null - задать пустое значение параметра{agree}):")
        else:
            print("\nСписка целей из Яндекс-Метрики нет. Можно ввести их вручную.")
            print("\nВведите через запятую пары чисел по форме:")
            print("[номер цели (1, 2 или 3)]:[номер цели в ЯндексМетрике],...")
            print("Например: 1:123543,2:9999933,3:2839463")
            id_str = input(f"(0 - выход из программы, null - задать пустое значение параметра{agree}):")

        # Пользователь ввел метку - ручной ввод
        flag_manual = False
        if id_str[:6] == "manual":
            id_str = id_str[6:]
            flag_manual = True

        # enter - согласиться с текущим значением
        if id_str == "" and agree != '':
            break
        elif id_str == '0':
            exit_programm()
        elif id_str == 'null':
            report_param_dic['Goals'] = ""
            break
        else:
            # Обработка введенного списка чисел
            try:
                # Приводим строку к формату СЛОВАРЬ
                id_str = id_str.replace(":", "':").replace(",", ",'")
                id_str = "'" + id_str
                id_str = "{" + id_str + "}"
                id_str = id_str.replace("'", '"')
                tmp_goals_dic = json.loads(id_str)

                if flag_all_goals_list and flag_manual == False :
                    current_dic = {key: all_goals_dic_dic[tmp_goals_dic[key]][0] for key in tmp_goals_dic}
                else:
                    current_dic = { key:  str(tmp_goals_dic[key]) for key in tmp_goals_dic }


                # Проверка на то, что ПОРЯДКОВЫЙ номер ЦЕЛИ - не более 3-х!!!
                for key in current_dic:
                    if int(key) not in [1,2,3]:
                        print(f"\nОшибка! Некорректный словарь чисел! Есть ключ цели с индексом {int(key)}!")
                        continue

            except:
                print("\nОшибка! Некорректный словарь чисел!")
                continue

        # Сохраняем результат в текущем словаре
        report_param_dic['Goals'] = str({ key.strip(): current_dic[key].strip() for key in current_dic })

    # ***
    # *** ШАГ 7 - Выбор AttributionModels **********************************************
    # Атрибуцию задаем ТОЛЬКО, если емть ЦЕЛИ !!!
    if report_param_dic['Goals'] != "":
        AttributionModels_dic = {1: 'LYDC', 2: 'LSC', 3: 'LC', 4: 'FC'}
        while True:
            print("\n", "*** ШАГ 7: Выбрать AttributionModels - модель атрибуции ***")
            for el in AttributionModels_dic:
                print(f"{el:1d}", AttributionModels_dic[el])

            try:
                if report_param_dic['AttributionModels'] != None:
                    print(f"\n{report_param_dic['AttributionModels']} - текущее значение этого параметра")
                    agree = ', [enter] - согласиться с текущим значением'
                else:
                    agree = ''
            except:
                agree = ''

            print("Можно ввести несколько моделей атрибуции, но необходимо иметь ввмду, что по каждой модели атрибуции - отдельный запрос, пишется всё в одну таблицу")
            id_str = input(
                f"Введите через запятую числа (0 - выход из программы, null - задать пустое значение параметра{agree}):")

            # enter - согласиться с текущим значением
            if id_str == "" and agree != '':
                break
            elif id_str == '0':
                exit_programm()
            elif id_str == 'null':
                report_param_dic['AttributionModels'] = ""
                break
            else:
                # Обработка введенного списка чисел
                try:
                    index_list = id_str.split(",")
                    index_list = [int(x) for x in index_list]
                    current_set = set([AttributionModels_dic[i] for i in index_list])
                except:
                    print("\nОшибка! Некорректный список чисел!")
                    continue

            # Сохраняем результат в текущем словаре
            l = list(current_set)
            l.sort()
            report_param_dic['AttributionModels'] = ", ".join(l)
    else:
        # Если целенй - нет, ТО И МОДЕЛЕЙ АТРИБУЦИИ НЕТ
        report_param_dic['AttributionModels'] = ""

    # # ***
    # # *** ШАГ 7 - Выбор AttributionModels **********************************************
    # # Атрибуцию задаем ТОЛЬКО, если емть ЦЕЛИ !!!
    # if report_param_dic['Goals'] != "":
    #     AttributionModels_dic = {1:'LYDC', 2:'LSC', 3:'LC', 4:'FC'}
    #     while True:
    #         print("\n", "*** ШАГ 7: Выбрать AttributionModels - модель атрибуции ***")
    #         for el in AttributionModels_dic:
    #             print(f"{el:1d}", AttributionModels_dic[el])
    #
    #         try:
    #             print(f"\n{report_param_dic['AttributionModels']} - текущее значение этого параметра")
    #             agree = ', [enter] - согласиться с текущим значением'
    #         except:
    #             agree = ''
    #
    #         id_str = input(f"Введите чиcло (0 - выход из программы{agree}):")
    #
    #         # enter - согласиться с текущим значением
    #         if id_str == "" and agree != '':
    #             break
    #
    #         if id_str == '0':
    #             exit_programm()
    #
    #         try:
    #             id = int(id_str)
    #             # Проверяем - есть такое значение  + сохраним
    #             report_param_dic['AttributionModels'] = AttributionModels_dic[id]
    #             break
    #         except:
    #             print("\nВы ошиблись, такого значения AttributionModels нет!")
    #             continue
    # else:
    #     # Если целей - нет, ТО И МОДЕЛЕЙ АТРИБУЦИИ НЕТ
    #     report_param_dic['AttributionModels'] = ""


    # Печатаем в конце все параметры
    print("\n*** Параметры запроса ***\n")
    print_parameters_report(parameter_name_list, global_fields_dic, report_param_dic)

    # ***
    # *** Запускаем report на выполнение
    id_str = input(f"\n[enter] - запускаем запрос на выполнение (0 - выход из программы):")
    if id_str == '0':
        exit_programm()

    return report_param_dic

def write_report_param_to_db(credential_bd, report_param_dic):
    """
    Записываем параметры текущего report - в БД
    Входные параметры:
    - credential_bd - параметры доступа к БД
    - report_param_dic - словарь параметров
    """
    tmp_dic = {}
    for k,v in report_param_dic.items():
        tmp_dic[k] = [v]   # в виде списка
    # Текущая дата-время
    tmp_dic['log_datetime'] = [datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
    # Из словаря делаем датафрейм
    df = pd.DataFrame.from_dict(tmp_dic)
    # Переводим наименование колонок в нижний регистр
    df.columns = df.columns.str.lower()
    # Удаляем лишние столбцы
    df.drop(['account', 'token', 'reporttype', 'all_goals_dic'], axis=1, inplace=True)
    # Пишем в БД
    print("Сохраняем параметры выполненного запроса в БД для последующего использования.")
    add_to_table_YD(credential_bd, 'parameters_report', df)
