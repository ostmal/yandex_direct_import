from src.import_from_YD import *
from src_many_reports.create_report_param import *

import pandas as pd
import datetime
import time
import yaml
import json


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

# ***
# *** Запускаем процедуру диалога с пользователем - для формирования параметров запроса
# TODO - расскоментировать
report_param_dic = create_report_param(credential_bd)


account = report_param_dic['account']
token = report_param_dic['token']
all_goals_dic = report_param_dic['all_goals_dic']
ReportType = report_param_dic['ReportType']
Report_id = report_param_dic['Report_id']
DateRangeType = report_param_dic['DateRangeType']
DateFrom = report_param_dic['DateFrom']
DateTo = report_param_dic['DateTo']
FieldNames = report_param_dic['FieldNames']
Filters = report_param_dic['Filters']
Goals = report_param_dic['Goals']
AttributionModels = report_param_dic['AttributionModels']

# ***
# *** Создаем таблицу (если она еще не создана) **************************************************************************
create_table(credential_bd, ReportType)

try:
    # Преобразуем Goals в словарь
    Goals_dic = json.loads(Goals.replace("'", '"'))
    Goals_list = [Goals_dic[key] for key in Goals_dic]
except:
    pass

# ***
# *** Создание тела запроса ********************************************
body = {
    "params": {
        "SelectionCriteria": {},
        "Page": {},
    }
}

body['params']['ReportType'] = ReportType
body['params']['DateRangeType'] = DateRangeType
if DateRangeType == "CUSTOM_DATE":
    body['params']['SelectionCriteria']['DateFrom'] = pd.to_datetime(DateFrom).strftime('%Y-%m-%d')
    body['params']['SelectionCriteria']['DateTo'] = pd.to_datetime(DateTo).strftime('%Y-%m-%d')

# Распарсиваем по ЗАПЯТОЙ - может быть несколько условий
body['params']['FieldNames'] = list(map(str.strip, FieldNames.split(",")))

# Формат, как задается фильтр
# https://yandex.ru/dev/direct/doc/examples-v5/python3_requests_stat2.html

if Filters != "":
    tmp = Filters
    tmp.replace("},{", "}${")
    tmp = tmp.split("$")
    Filters_list_json = list(map(json.loads, tmp))
    body['params']['SelectionCriteria']['Filter'] = Filters_list_json

try:
    if Goals_list != []:
        body['params']['Goals'] = Goals_list
except:
    Goals_dic = []

try:
    if Goals_list != []:
        if AttributionModels == "" or AttributionModels == None:
            # Эта модель атрибуции применяется по умолчанию. Здесь это необходио, чтобы писать в БД
            AttributionModels = ['LYDC']
        else:
            AttributionModels = AttributionModels.split(",")
            AttributionModels = list(map(strip, AttributionModels))
except:
    pass

body['params']['Format'] = "TSV"
# НДС - включать
body['params']['IncludeVAT'] = "YES"
body['params']['IncludeDiscount'] = "YES"

table_name = credential_bd['table_prefix'] + ReportType.lower()


if AttributionModels == "" or AttributionModels == None:
    # Эта модель атрибуции применяется по умолчанию. Здесь это необходио, чтобы писать в БД
    AttributionModels = ['LYDC']

time_start = time.perf_counter()

# для логирования
log_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Перебираем все модели атрибуции и "склеиваем таблицы"
for el in AttributionModels:
    body['params']['AttributionModels'] = [el.strip()]
    # *** ЗАПРОС к Яндекс-Директ ****************************************************************
    import_from_YD_1000000(log_datetime, account, token, body,table_name, config, credential_bd, Goals_dic)



# ***
# *** Записываем параметры текущего report - в БД ********************************************

# Это делается после запроса, поскольку запрос может быть составлен некорректно - чтобы не писать в БД некорректный запрос
write_report_param_to_db(credential_bd, report_param_dic)

time_finish = time.perf_counter()
print(f"Время работы программы:  {time_finish - time_start:0.1f} секунд")