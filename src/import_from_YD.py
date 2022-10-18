from src.data_transform_raw import *
from src.add_to_table_YD import *
from src_many_reports.data_transform import *

import pandas as pd
import datetime
import requests
import json
from requests.exceptions import ConnectionError
from time import sleep
import sys
import logging

def import_from_YD_1000000(log_datetime, login_yd, token, body, table_name, config, credential_bd, goals):
    """
    Использует базовый запрос - import_from_YD
    Но, в Яндекс_директ есть ограничения на 1 млн, поэтому считываент фреймы и записывает их в БД  и CSV- файл (уакзано в конфиг файле)
    """
    logging.info(f"Запускаем запрос с параметрами: {body}")
    Limit = 1000000  # Можно брать и больше, но может зависнуть. По-умолчаниө - 1 млн.
    Offset = 1  # Правильнее - 0, но имеется баг - система с нулем не работает
    while True:
        logging.info(f"New Page, Offset: {Offset}, Limit: {Limit}")
        body['params']['Page']['Limit'] = Limit
        body['params']['Page']['Offset'] = Offset
        body['params']['ReportName'] = f"YD___{str(datetime.datetime.now())}"
        req = import_from_YD(token, body)

        # *** Ищем в ответе - кол-во выводимых строк (чтобы понять, что у нас уже последний фрейм)
        data_list = req.text.split("\n")[2:]
        # Распарсим Total rows
        sub = 'total rows'

        row_count = int(data_list[-2].split(":")[1].strip())
        logging.info(f"row_count: {row_count}")

        if row_count == 0:
            logging.info("Последний фрейм - нулевой, заканчиваем...")
            break

        # Определяем: какая таблица, чтобы выбрать функцию обработки
        if table_name[-3:] == "big":
            df = data_transform_big(req, log_datetime, login_yd, goals)
        else:
            df = data_transform_many_reports(req, log_datetime, login_yd, body, goals)

        # Проверяем файл конфигурации: записывать в CSV-файл?
        if config['write_to_csv']:
            now = datetime.datetime.now()
            tmp = now.strftime("%Y-%m-%d__%H-%M")
            df.to_csv(f"{config['path_csv']}{table_name}_{tmp}.csv", sep=";", decimal=',', mode='a',
                      encoding='utf-8-sig',
                      index=False)
        else:
            # Добавление данные из ДатаФрейма в таблицу БД
            add_to_table_YD(credential_bd, table_name, df)

        # *** Проверим row_count - и продолжаем, если он еһе болғшој
        if row_count == Limit:
            logging.info("Размер фрейма: row_count == Limit , Берем следующий  фрейм...")
            Offset += Limit
        else:
            logging.info("Размер фрейма: row_count != Limit , заканчиваем...")
            break




def import_from_YD(token,body):
    """
    Импортируем данные из Яндекс-Директ в ДатаФрейм
    """
    # Метод для корректной обработки строк в кодировке UTF-8 как в Python 3, так и в Python 2
    if sys.version_info < (3,):
        def u(x):
            try:
                return x.encode("utf8")
            except UnicodeDecodeError:
                return x
    else:
        def u(x):
            if type(x) == type(b''):
                return x.decode('utf8')
            else:
                return x

    # --- Входные данные ---
    # Адрес сервиса Reports для отправки JSON-запросов (регистрозависимый)
    ReportsURL = 'https://api.direct.yandex.com/json/v5/reports'

    # OAuth-токен пользователя, от имени которого будут выполняться запросы
    # token = 'ТОКЕН'

    # Логин клиента рекламного агентства
    # Обязательный параметр, если запросы выполняются от имени рекламного агентства
    # clientLogin = 'ЛОГИН_КЛИЕНТА'

    # --- Подготовка запроса ---
    # Создание HTTP-заголовков запроса
    headers = {
        # OAuth-токен. Использование слова Bearer обязательно
        "Authorization": "Bearer " + token,
        # Логин клиента рекламного агентства
        # "Client-Login": clientLogin,
        # Язык ответных сообщений
        "Accept-Language": "ru",
        # Режим формирования отчета
        "processingMode": "auto",
        # Формат денежных значений в отчете - Если ракомментировать - то укажет реальные данные
        "returnMoneyInMicros": "false",
        # Не выводить в отчете строку с названием отчета и диапазоном дат
        # "skipReportHeader": "true",
        # Не выводить в отчете строку с названиями полей
        # "skipColumnHeader": "true",
        # Не выводить в отчете строку с количеством строк статистики
        # "skipReportSummary": "true"
    }

    # Кодирование тела запроса в JSON
    body = json.dumps(body, indent=4)

    # --- Запуск цикла для выполнения запросов ---
    # Если получен HTTP-код 200, то выводится содержание отчета
    # Если получен HTTP-код 201 или 202, выполняются повторные запросы
    while True:
        try:
            req = requests.post(ReportsURL, body, headers=headers)
            print("Запрос post - отработал")
            req.encoding = 'utf-8'  # Принудительная обработка ответа в кодировке UTF-8
            if req.status_code == 400:
                print("Параметры запроса указаны неверно или достигнут лимит отчетов в очереди")
                print("RequestId: {}".format(req.headers.get("RequestId", False)))
                print("JSON-код запроса: {}".format(u(body)))
                print("JSON-код ответа сервера: \n{}".format(u(req.json())))
                break
            elif req.status_code == 200:
                print("Отчет создан успешно")
                print("RequestId: {}".format(req.headers.get("RequestId", False)))
                # print("Содержание отчета: \n{}".format(u(req.text)))
                break
            elif req.status_code == 201:
                print("Отчет успешно поставлен в очередь в режиме офлайн")
                retryIn = int(req.headers.get("retryIn", 60))
                print("Повторная отправка запроса через {} секунд".format(retryIn))
                print("RequestId: {}".format(req.headers.get("RequestId", False)))
                sleep(retryIn)
            elif req.status_code == 202:
                print("Отчет формируется в режиме офлайн")
                retryIn = int(req.headers.get("retryIn", 60))
                print("Повторная отправка запроса через {} секунд".format(retryIn))
                print("RequestId:  {}".format(req.headers.get("RequestId", False)))
                sleep(retryIn)
            elif req.status_code == 500:
                print("При формировании отчета произошла ошибка. Пожалуйста, попробуйте повторить запрос позднее")
                print("RequestId: {}".format(req.headers.get("RequestId", False)))
                print("JSON-код ответа сервера: \n{}".format(u(req.json())))
                break
            elif req.status_code == 502:
                print("Время формирования отчета превысило серверное ограничение.")
                print(
                    "Пожалуйста, попробуйте изменить параметры запроса - уменьшить период и количество запрашиваемых данных.")
                print("JSON-код запроса: {}".format(body))
                print("RequestId: {}".format(req.headers.get("RequestId", False)))
                print("JSON-код ответа сервера: \n{}".format(u(req.json())))
                break
            else:
                print("Произошла непредвиденная ошибка")
                print("RequestId:  {}".format(req.headers.get("RequestId", False)))
                print("JSON-код запроса: {}".format(body))
                print("JSON-код ответа сервера: \n{}".format(u(req.json())))
                break

        # Обработка ошибки, если не удалось соединиться с сервером API Директа
        except ConnectionError:
            # В данном случае мы рекомендуем повторить запрос позднее
            print("Произошла ошибка соединения с сервером API. Рекомендуем повторить запрос позднее")
            # Принудительный выход из цикла
            break

        # Если возникла какая-либо другая ошибка
        except:
            # В данном случае мы рекомендуем проанализировать действия приложения
            print("Произошла непредвиденная ошибка. В данном случае мы рекомендуем проанализировать действия приложения")
            # Принудительный выход из цикла
            break
    return req