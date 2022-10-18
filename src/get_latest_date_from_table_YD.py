import psycopg2
import logging

def get_latest_date_from_table_YD(credential_bd, field_date='date'):
    """
    Вытащить последнюю дату из текущей таблицы
    """
    logging.info("Вытаскиваем последнюю дату из текущей таблицы")
    # Соединение к PostgreSQL
    con = psycopg2.connect(
        database=credential_bd['database'],
        user=credential_bd['user'],
        password=credential_bd['password'],
        host=credential_bd['host']
    )

    cursor =con.cursor()
    sql = f"SELECT max({field_date})  FROM {credential_bd['schema']}.{credential_bd['table_name']};"
    cursor.execute(sql)
    # Получаем строки с данными
    rows = cursor.fetchall()
    # Закрываем соединение
    con.close()

    try:
        return rows[0][0].strftime('%Y-%m-%d')
    except:
        return '2022-04-01'