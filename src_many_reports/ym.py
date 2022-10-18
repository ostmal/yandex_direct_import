import pandas as pd
import requests
import json


from tapi_yandex_metrika import YandexMetrikaLogsapi

def get_goal_table(counter_id, header, request_url, out='var'):
    """
    Функция просмотра всех целей в табличном формате
    """
    request_goal = request_url['goals'].format(counter_id)
    res = requests.get(request_goal, headers=header)
    res_json = json.loads(res.content)
    goals_df = pd.json_normalize(res_json['goals'])
    goals_df['counter_id'] = counter_id
    if out == 'var':
        return goals_df
    elif out == 'csv':
        goals_df.to_csv('goals_{}'.format(counter_id), index=False)