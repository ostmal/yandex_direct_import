from src_many_reports.create_dic import *

import pandas as pd
import psycopg2
from sqlalchemy import create_engine


def read_from_db(credential_bd, sql):
    """
    Вытащить список аккаунтов
    """
    # Соединение к PostgreSQL
    con = psycopg2.connect(
        database=credential_bd['database'],
        user=credential_bd['user'],
        password=credential_bd['password'],
        host=credential_bd['host']
    )

    cursor = con.cursor()

    cursor.execute(sql)

    # Получаем названия столбцов
    column_names = [desc[0] for desc in cursor.description]

    # Получаем строки с данными
    rows = cursor.fetchall()

    # Изменения сохраняются в БД
    con.commit()

    # Закрываем соединение
    con.close()

    df = pd.DataFrame(rows, columns=column_names)
    return df


def write_to_db(credential_bd, sql):
    """
    Запрос на запись в БД
    """
    # Соединение к PostgreSQL
    con = psycopg2.connect(
        database=credential_bd['database'],
        user=credential_bd['user'],
        password=credential_bd['password'],
        host=credential_bd['host']
    )

    cursor = con.cursor()

    cursor.execute(sql)

    # Изменения сохраняются в БД
    con.commit()

    # Закрываем соединение
    con.close()



def create_table(credential_bd, tbl_name):
    """
    Создаем таблицу для many_reports (для одного из 8 отчетов)
    Входные параметры
    - credential_bd
    - tbl_name - наименование отчета (оно же - наименование таблицы)

    ВАЖНО!!!
    Несмотря на то, что пользователь перед запуском программы может указывать ОПРЕДЕЛЕННЫЕ поля - создаются ВСЕ поля,
    которые могут присутствовать в данном отчете !!!
    """
    fields_special_list = ['ConversionRate', 'Conversions', 'CostPerConversion', 'GoalsRoi', 'Revenue']

    fields_dic = create_fields_dic()[tbl_name]

    # Соединение к PostgreSQL
    con = psycopg2.connect(
        database=credential_bd['database'],
        user=credential_bd['user'],
        password=credential_bd['password'],
        host=credential_bd['host']
    )

    print(credential_bd)
    cursor = con.cursor()
    sql = f'''
        CREATE TABLE IF NOT EXISTS {credential_bd['schema']}.{credential_bd['table_prefix']}{tbl_name} (
            id SERIAL PRIMARY KEY,
            account VARCHAR,
            log_datetime timestamp,
            attributionmodels VARCHAR,
    '''

    for k, v in fields_dic.items():

        fields_special_list
        if v in [ 'сегмент', 'атрибут']:
            sql += f"{k} VARCHAR,"
        if v == 'метрика':
            if k in fields_special_list:   # это специальное поле и его надо утраивать...
                for n in range(1,4):
                    sql += f"{k}_{str(n)} NUMERIC,"
            else:
                sql += f"{k} NUMERIC,"

    sql = sql[:-1]
    sql += ");"

    cursor.execute(sql)
    con.commit()
    # Закрываем соединение
    con.close()