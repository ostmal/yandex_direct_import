import psycopg2
import logging

def create_table(credential_bd, tbl_name, fields, goals, fields_additional=""):
    """
    Создаем таблицу в PostgreSQL
    """
    # Создадим строку, вида "ИмяПоля Тип,"
    str_fields = " ".join([f"{el} {fields[el]}," for el in fields])

    # Создадим дополнительные поля, если указаны ЦЕЛИ
    try:
        list_Goal = goals['Goals']
        try:
            list_AttributionModels = goals['AttributionModels']
        except:
            list_AttributionModels = ["LYDC"]   # В ЯД - тоже такое же значение по-умолчанию

        str_fields_Conversions = ""
        for goal in list_Goal:
            for attr in list_AttributionModels:
                str_fields_Conversions += f"Conversions_{goal}_{attr} INT,"

    except:
        str_fields_Conversions = "Conversions INT,"



    # Соединение к PostgreSQL
    con = psycopg2.connect(
        database=credential_bd['database'],
        user=credential_bd['user'],
        password=credential_bd['password'],
        host=credential_bd['host']
    )

    cursor = con.cursor()
    sql = f'''
        CREATE TABLE IF NOT EXISTS {credential_bd['schema']}.{tbl_name} (
            id SERIAL PRIMARY KEY,
            account VARCHAR,
            log_datetime timestamp,
            Date DATE,
            CampaignId INT,
            CampaignName VARCHAR,

            {str_fields}

            Impressions INT,  
            Clicks INT,  
            {str_fields_Conversions}
            Cost numeric
            
            {fields_additional}

            );
    '''

    cursor.execute(sql)
    con.commit()
    # Закрываем соединение
    con.close()