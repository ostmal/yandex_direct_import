import pandas as pd
import logging
import datetime

def data_transform_big(req, log_datetime, login, goals):
    """
    raw-данные
    Обрабатываем данные из Яндекс-Директ в ДатаФрейм
    """
    # *********** ОБРАБОТКА ДАННЫХ *******************************************
    logging.info("raw-данные - обрабатываем данные в ДатаФрейме")
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

    # Последние ячейки - to_numeric
    df[['Impressions', 'Clicks', 'Cost']] = df[['Impressions', 'Clicks', 'Cost']].apply(pd.to_numeric, errors='coerce')

    # Обработка полей "Conversions"... - переводим в тип numeric
    try:
        list_Goal = goals['Goals']
        try:
            list_AttributionModels = goals['AttributionModels']
        except:
            list_AttributionModels = ["LYDC"]   # В ЯД - тоже такое же значение по-умолчанию

        for goal in list_Goal:
            for attr in list_AttributionModels:
                fields_Conversions = f"Conversions_{goal}_{attr}"
                df[fields_Conversions] = df[fields_Conversions].apply(pd.to_numeric, errors='coerce')
    except:
        df['Conversions'] = df['Conversions'].apply(pd.to_numeric, errors='coerce')

    # Записываем значение account **********************************************
    df['account'] = login

    # Записываем значение полей  year-month  **********************************************
    # df['year'] = pd.to_datetime(df['Date']).dt.year
    # df['month'] = pd.to_datetime(df['Date']).dt.month

    # Записываем значение log_datetime - текущая дата-время (логирование) *****************************
    df['log_datetime'] = log_datetime

    # Переводим наименование колонок в нижний регистр
    df.columns = df.columns.str.lower()

    # Сортируем
    df = df.sort_values(['date', 'campaignid'])

    # print(df.columns)
    # print(df.info())

    return df