from src_many_reports.ym import *
from src_many_reports.operations_with_database import *
from src_many_reports.code_optimization import *
from src_many_reports.different_procedures import *

import yaml
import datetime

print("***********************************************************")
print("*** Скрипт для получения списка целей из Яндекс-Метрики +++")
print("***********************************************************")

ACCESS_TOKEN = input("Введите токен от Яндекс-Метрики:")
COUNTER_ID = input("Введите номер счетчика:")

# Считывание параметров доступа к БД
with open(r'etc\credential_bd_many_reports.yml') as file:
    credential_bd = yaml.load(file, Loader=yaml.FullLoader)

# ***
# *** Делаем запрос к Яндекс - Метрике - считываем ЦЕЛИ ************************************
HEADERS = {"Authorization": "Bearer " + ACCESS_TOKEN}
request_url = {
    #get stats
    'stat': 'https://api-metrika.yandex.net/stat/v1/data',
    #get goals
    'goals': 'https://api-metrika.yandex.net/management/v1/counter/{}/goals',
    # Evaluating a request
    'evaluate': 'https://api-metrika.yandex.ru/management/v1/counter/{}/logrequests/evaluate',
    # Request for data
    'log_request': 'https://api-metrika.yandex.ru/management/v1/counter/{}/logrequests',
    # Check status
    'download': 'https://api-metrika.yandex.ru/management/v1/counter/{}/logrequest/{}/part/{}/download',
    # Clean after downloaded
    'clean': 'https://api-metrika.yandex.net/management/v1/counter/{}/logrequest/{}/clean?'
}

try:
    df = get_goal_table(COUNTER_ID, HEADERS, request_url)
    print("\n*** Список целей ***\n")
    print(df[['id', 'name']].to_string(index=False))
    print(f"\nСчитано - {df.shape[0]} целей")
except:
    print("Считывание целей прошло неудачно!. Выход из программы.")


# ***
# *** Создадим словарь целей для записи в БД *****************************
goals_dic = {}
for row in df.itertuples():
    tmp = row.name
    tmp = tmp.replace("'", '*')
    tmp = tmp.replace("“", '*')
    tmp = tmp.replace("”", '*')
    tmp = tmp.replace('"', '*')
    goals_dic[f"{row.id}"] = tmp



# ***
# *** Считываю список аккаунтов **********************************************
sql = f"SELECT account_id, organization_name, account, token, goals, goals_log_date FROM {credential_bd['schema']}.accounts;"
df_accounts = read_from_db(credential_bd, sql)
# Переименуем столбцы
df_accounts = df_accounts.rename(columns={'account_id': 'id'})
df_accounts['id'] = df_accounts['id'].astype(int)
df_accounts = df_accounts.set_index('id')

while True:
    print("\n","*** Записать полученные из Яндекс-Метрики цели в соответствующий аккаунт Яндекс Директа в БД ***")
    print(df_accounts[['organization_name', 'account']])

    id_str = input("Введите чиcло - номер аккаунта Яндекс-Директа для записи (0 - выход из программы):")
    if id_str == '0':
        exit_programm()

    try:
        id = int(id_str)
        # Проверяем - такой аккаунт есть?
        df_accounts.loc[id]
        break
    except:
        print("\nВы ошиблись, такого аккаунта в списке нет!")
        continue


# ***
# *** Выводим на экран СПИСОК ЦЕЛЕЙ у этого аккаунта Яндекс-Директ *****
goals_in_bd = df_accounts.loc[id]['goals']

print(goals_in_bd)

if (goals_in_bd != "" and  goals_in_bd != 'None' and goals_in_bd == 'NULL'):
    # Обнаружено, что в аккаунте уже есть список целей!
    print("\nВнимание! В этом аккаунте уже есть список целей:")
    all_goals_dic_dic = print_goals_list(goals_in_bd)
    print(f"\nВнимание! В этом аккаунте уже есть список целей (см.выше), всего - {len(all_goals_dic_dic)} целей!")
    print(f"{df_accounts.loc[id]['goals_log_date']} - дата-время, когда он был записан в БД")

    print("\nПерезаписать?")
    id_str = input(f"yes - перезаписать,  другое - выход из программы:")
    if id_str != 'yes':
        print("\nСписок целей в БД (таблица аккаунтов Яндекс-Директ) остался неизменным.")
        exit_programm()


# ***
# *** Сохраним в БД ***********************************************
dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
d =  "{" + ','.join('"{}":"{}"'.format(key, val) for key, val in goals_dic.items()) + "}"
sql = f"update {credential_bd['schema']}.accounts set goals = '{d}', goals_log_date = '{dt}' where account_id = {id};"
write_to_db(credential_bd, sql)
print("\nСписок целей записан в БД.")


