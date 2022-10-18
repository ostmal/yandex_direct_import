from src.create_table import create_table
from src.get_latest_date_from_table_YD import get_latest_date_from_table_YD
from src.import_from_YD import *


import pandas as pd
import yaml
from datetime import date
import datetime
import sys
import time
import logging


# Настройка логирования
file_log = logging.FileHandler('Log.log')
console_out = logging.StreamHandler()
logging.basicConfig(handlers=(file_log, console_out),
                    format='[%(asctime)s | %(module)s | %(funcName)s | %(levelname)s]: %(message)s',
                    datefmt='%m.%d.%Y %H:%M:%S',
                    level=logging.INFO)

# Считывание параметров конфигурации
with open(r'etc\config.yml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

# Считывание параметров доступа к БД
with open(r'etc\credential_bd.yml') as file:
    credential_bd = yaml.load(file, Loader=yaml.FullLoader)

# Считывание параметров доступа к Яндекс-Директ
with open(r'etc\credential_YD.yml') as file:
    credential_YD = yaml.load(file, Loader=yaml.FullLoader)
token = credential_YD['token']

# Считывание списка полей запроса
with open(r'etc\fields.yml') as file:
    fields = yaml.load(file, Loader=yaml.FullLoader)

# Считывание списка целей (+ модель атрибуции)
with open(r'etc\goals.yml') as file:
    goals = yaml.load(file, Loader=yaml.FullLoader)

table_name = credential_bd['table_prefix'].lower() + credential_bd['table_name'].lower() + "_big"

#
# *** Создание таблицы
create_table(credential_bd, table_name, fields, goals)   # Создание таблицы RAW


# Проверяем файл конфигурации: период задается вручную?
if config['date_range']:
    DateFrom = input("Введите начальную дату в формате YYYY-MM-DD: ")
    DateTo = input("Введите конечную дату в формате YYYY-MM-DD: ")
    DateFrom = pd.to_datetime(DateFrom)
    DateTo = pd.to_datetime(DateTo)
else:
    # Ищем последнюю дату в текущей таблице
    latest_date = get_latest_date_from_table_YD(credential_bd)
    logging.info(f"Последняя дата в текущей таблице - {latest_date}")

    # DateFrom: latest_date+1day
    DateFrom = pd.to_datetime(latest_date) + pd.DateOffset(1)
    # DateTo - вчерашняя дата
    DateTo = (date.today()- pd.DateOffset(1))

time_start = time.perf_counter()

# Проверяем, что начальная дата не превосходит начальную
if DateFrom > DateTo:
    print("В базе данных есть последние данные! Обновление не требуется! Выход из программы.")
    sys.exit()

# Приводим дату к строке
DateFrom = DateFrom.strftime('%Y-%m-%d')
DateTo = DateTo.strftime('%Y-%m-%d')


#
# *** ИМПОРТИРУЕМ - ОБРАБАТЫВАЕМ - ЗАПИСЫВАЕМ RAW-данные
# Импортируем последние данные из ЯндексДирект - большая таблица 

# Обрабатываем FieldNames
FieldNames =  ( [f"{el}" for el in fields] )
FieldNames = FieldNames + ["Date", "CampaignId", "CampaignName", "Impressions", "Clicks", "Conversions", "Cost"]

# Обрабатываю поля "ЦЕЛИ"
try:
    AttributionModels = goals['AttributionModels']
except:
    AttributionModels = []
try:
    Goals = goals['Goals']
except:
    Goals = []
    AttributionModels = []

# ***
# *** Создание тела запроса ********************************************
body = {
    "params": {
        "SelectionCriteria": {},
        "Page": {},
    }
}

body['params']['ReportType'] = "CUSTOM_REPORT"
body['params']['DateRangeType'] = "CUSTOM_DATE"
body['params']['SelectionCriteria']['DateFrom'] = DateFrom
body['params']['SelectionCriteria']['DateTo'] = DateTo
body['params']['FieldNames'] = FieldNames
# body['params']['SelectionCriteria']['Filter'] = [{"Field": "Clicks","Operator": "GREATER_THAN","Values": ["0"]},]
body['params']['Goals'] = Goals
body['params']['AttributionModels'] = AttributionModels

body['params']['Format'] = "TSV"
# НДС - включать
body['params']['IncludeVAT'] = "YES"
body['params']['IncludeDiscount'] = "YES"


time_start = time.perf_counter()

# для логирования
log_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

import_from_YD_1000000(log_datetime, credential_YD['login'], token, body,table_name, config, credential_bd, goals)

time_finish = time.perf_counter()
print(f"Время работы программы:  {time_finish - time_start:0.1f} секунд")
