from src_many_reports.create_dic import *

import pandas as pd
import logging
import datetime

def data_transform_many_reports(req, log_datetime, login_yd, body, goals):
    """
    Обрабатываем данные из Яндекс-Директ в ДатаФрейм
    login_yd, body - необходимы для записи
    goals -  словарь целей
    """
    # *********** ОБРАБОТКА ДАННЫХ *******************************************
    logging.info("обрабатываем данные в ДатаФрейме")
    # Наименование колонок
    columns = req.text.split("\n")[1].split('\t')

    # Данные
    data_list = req.text.split("\n")[2:]
    data = [x.split("\t") for x in data_list]

    # Делаем датафрейм
    df = pd.DataFrame(data, columns=columns)

    # Удаляем строки с  пустой строкой в конце
    if df.iloc[-1][0] == "":
        df = df[:-1]

    # Удаляем строки с  "Total rows"
    if df.iloc[-1][0][:10] == "Total rows":
        df = df[:-1]

    # Меняем все значения "--" на ""
    df = df.replace("--", "")

    # Записываем значение account **********************************************
    df['account'] = login_yd

    # Записываем значение log_datetime - текущая дата-время (логирование) *****************************
    df['log_datetime'] = log_datetime

    # Переводим наименование колонок в нижний регистр
    df.columns = df.columns.str.lower()

    # attributionmodels - заводим модель атрибуции
    try:
        AttributionModels = body['params']['AttributionModels'][0]
        df['attributionmodels'] = AttributionModels
    except:
        pass
    # Переименовываем 5 специальных полей
    rename_columns_dic = {}
    fields_special_list = ['conversionrate', 'conversions', 'costperconversion', 'goalsroi', 'revenue']
    try:   # Если есть Атрибуция и Цели
        tmp = body['params']['Goals']
        for fields_special in fields_special_list:
            for  k,v in goals.items():
                rename_columns_dic[f"{fields_special}_{v}_{AttributionModels.lower()}"] = f"{fields_special}_{k}"
    except:
        # Переименовываеи специальные поля в СпецПоле_1
        for fields_special in fields_special_list:
            rename_columns_dic[f"{fields_special}"] = f"{fields_special}_1"


    # print(f"rename_columns_dic --- {rename_columns_dic}")
    df = df.rename(columns=rename_columns_dic)

    # ***
    # *** Переводим поля с метриками в тип numeric *********************************

    # 1. Считываем все поля метрики по этому отчету ( в т.ч. специальные - они могут быть в таблице, емли нет целей)
    ReportType = body['params']['ReportType']
    all_fields_metric_set = set()
    fields_dic = create_fields_dic()[ReportType]
    for k, v in fields_dic.items():
        if v == 'метрика':
            all_fields_metric_set = all_fields_metric_set | {k.lower()}

    # 2. Добавляем Множество УТРОЕННЫХ специальных полей
    for k, v in rename_columns_dic.items():
        all_fields_metric_set = all_fields_metric_set | {v.lower()}
    # print(f"all_fields_metric_set --- {all_fields_metric_set}")

    # 3. Поля df - тоже переводим во множество
    df_columns_set = set(df.columns.to_list())
    # print(f"df_columns_set --- {df_columns_set}")

    # 4. Находим пересечение
    df_columns_metrics_set = all_fields_metric_set & df_columns_set
    # print(f"df_columns_metrics_set --- {df_columns_metrics_set}")

    # 5. Переводим в число
    df_columns_metrics_list = list(df_columns_metrics_set)
    df[df_columns_metrics_list] = df[df_columns_metrics_list].apply(pd.to_numeric, errors='coerce')

    return df