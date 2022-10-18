
def get_dictionary(name_dic):
    """
    Создание словарей
    """

    if name_dic == 'report_dic':
        return {    1: 'ACCOUNT_PERFORMANCE_REPORT',
                    2: 'AD_PERFORMANCE_REPORT',
                    3: 'ADGROUP_PERFORMANCE_REPORT',
                    4: 'CAMPAIGN_PERFORMANCE_REPORT',
                    5: 'CRITERIA_PERFORMANCE_REPORT',
                    6: 'CUSTOM_REPORT',
                    7: 'REACH_AND_FREQUENCY_PERFORMANCE_REPORT',
                    8: 'SEARCH_QUERY_PERFORMANCE_REPORT'}

    if name_dic == 'DateRangeType_dic':
        return {    1: 'CUSTOM_DATE',
                    2: 'TODAY',
                    3: 'YESTERDAY',
                    4: 'LAST_3_DAYS',
                    5: 'LAST_5_DAYS',
                    6: 'LAST_7_DAYS',
                    7: 'LAST_14_DAYS',
                    8: 'LAST_30_DAYS',
                    9: 'LAST_90_DAYS',
                    10: 'LAST_365_DAYS',
                    11: 'THIS_WEEK_MON_TODAY',
                    12: 'THIS_WEEK_SUN_TODAY',
                    13: 'LAST_WEEK',
                    14: 'LAST_BUSINESS_WEEK',
                    15: 'LAST_WEEK_SUN_SAT',
                    16: 'THIS_MONTH',
                    17: 'LAST_MONTH',
                    18: 'ALL_TIME',
                    19: 'AUTO', }

def get_fields_list(global_fields_dic, report_name, type_field='all', set_to_check=""):
    """
    Входные параметры:
    report_name
    type_field - тип field ('сегмент', 'атрибут', 'метрика'). Если 'all' - выбирать все поля
    current_full_fields_report_set - рассматривать только эти поля

    Работает в 2-х режимах
    1. (если current_full_fields_report_set == "") возвращает список полный field
    2. из входного списка выбирает только те  field, которые удовлетворяют типу type_field

    Выходной параметр - список field
    """

    fields_dic = global_fields_dic[report_name]

    fields_list = []
    # Получаем полный SET всех возможных полей данного типа
    for k, v in fields_dic.items():
        if type_field == 'all' or type_field == v:
            fields_list.append(k)
    fields_set = set(fields_list)

    # Режим 1. На входе нет пользовательского SET. Получим SET всех fields данного типа
    if set_to_check == "":
        return fields_set
    # Режим 2.  На входе ЕСТЬ пользовательский SET
    else:
        return set_to_check & fields_set

def selection_fields_plus_minus(operation, current_fields_set, full_fields_YD_set):
    """
    Функция реализует выбор из полей для ПЛЮСОВАНИЯ или МИНУСОВАНИЯ

    :param operation: операция - плюс или минус (добавить или отнять)
    :param current_fields_set: Текущий SET этого типа полей этого report
    :param full_fields_YD_set: Полный SET ВСЕХ ВОЗМОЖНЫХ полей из YD для этого report
    :return: новый Текущий SET этого типа полей этого report
    """

    if operation == "+":
        print("\n", "*** Добавить поля к имеющимся ***")
    else:
        print("\n", "*** Удалить поля из имеющихся ***")
    n = 0

    if operation == "+":
        for_choose_set = full_fields_YD_set - current_fields_set
    else:
        for_choose_set = current_fields_set

    for_choose_list = list(for_choose_set)
    for_choose_list.sort()
    for el in for_choose_list:
        n += 1
        print(f"{n:2d}", el)

    current_fields_list = list(current_fields_set)
    current_fields_list.sort()
    try:
        print(f"\n{current_fields_list} - текущее значение этого параметра")
    except:
        pass

    if operation == "+":
        tmp = "дополнительные поля"
    else:
        tmp = "удаляемые поля"
    id_str = input(f"Введите через запятую числа - {tmp} ([enter] - вернуться к выбору из списка):")

    # enter - согласиться с текущим значением
    if id_str == "":
        return current_fields_set

    try:
        index_list = id_str.split(",")
        index_list = [(int(x)-1) for x in index_list]
        delta_fields_set = set([for_choose_list[i] for i in index_list])
        if operation == "+":
            return (current_fields_set | delta_fields_set)
        else:
            return(current_fields_set - delta_fields_set)
    except:
        print("\nОшибка! Некорректный список чисел!")
        return current_fields_set

def fields_check(set_to_check):
    """
    Проверка fields на совместимость
    https://yandex.ru/dev/direct/doc/reports/compatibility.html

    :param set_to_check: SET полей для проверки
    :return: True - если все нормально.. Объявление - если Несовместимо
    """
    # Date, Week, Month, Quarter, Year являются взаимоисключающими
    set_1 = set(['Date', 'Week', 'Month', 'Quarter', 'Year'])
    if len(set_1 & set_to_check) > 1:
        return "Поля Date, Week, Month, Quarter, Year являются взаимоисключающими"

    # Поле ClickType несовместимо с полями Impressions, Ctr, AvgImpressionPosition,
    # WeightedImpressions, WeightedCtr, AvgTrafficVolume
    set_1 = set(['ClickType'])
    set_2 = set(['Impressions', 'Ctr', 'AvgImpressionPosition', 'WeightedImpressions', 'WeightedCtr', 'AvgTrafficVolume'])
    if len(set_1 & set_to_check) >= 1 and len(set_2 & set_to_check) >= 1:
        return "Поле ClickType несовместимо с полями Impressions, Ctr, AvgImpressionPosition, WeightedImpressions, WeightedCtr, AvgTrafficVolume"

    # Поле ImpressionShare несовместимо с полями AdFormat, AdId, Age, CarrierType,
    # Gender, MobilePlatform, RlAdjustmentId.
    set_1 = set(['ImpressionShare'])
    set_2 = set(['AdFormat', 'AdId', 'Age', 'CarrierType', 'Gender', 'MobilePlatform', 'RlAdjustmentId'])
    if len(set_1 & set_to_check) >= 1 and len(set_2 & set_to_check) >= 1:
        return "Поле ImpressionShare несовместимо с полями AdFormat, AdId, Age, CarrierType, Gender, MobilePlatform, RlAdjustmentId"

    return True


def create_fields_dic():
    """
    Создаем словарь словарей (имя report:{имя field: тип field}
    1-й уровень ключей - Наименования report
    2-й уровень: Наименование field: Тип поля (сегмент, атрибут, метрика)
    """
    return {
        'ACCOUNT_PERFORMANCE_REPORT':
            {
                'AdFormat': 'сегмент',
                'AdGroupId': '–',
                'AdGroupName': '–',
                'AdId': '–',
                'AdNetworkType': 'сегмент',
                'Age': 'сегмент',
                'AudienceTargetId': '–',
                'AvgClickPosition': 'метрика',
                'AvgCpc': 'метрика',
                'AvgCpm': '–',
                'AvgEffectiveBid': 'метрика',
                'AvgImpressionFrequency': '–',
                'AvgImpressionPosition': 'метрика',
                'AvgPageviews': 'метрика',
                'AvgTrafficVolume': 'метрика',
                'BounceRate': 'метрика',
                'Bounces': 'метрика',
                'CampaignId': '–',
                'CampaignName': '–',
                'CampaignUrlPath': '–',
                'CampaignType': 'сегмент',
                'CarrierType': 'сегмент',
                'Clicks': 'метрика',
                'ClickType': 'сегмент',
                'ClientLogin': 'сегмент',
                'ConversionRate': 'метрика',
                'Conversions': 'метрика',
                'Cost': 'метрика',
                'CostPerConversion': 'метрика',
                'Criteria': '–',
                'CriteriaId': '–',
                'CriteriaType': 'сегмент',
                'Criterion': '–',
                'CriterionId': '–',
                'CriterionType': 'сегмент',
                'Ctr': 'метрика',
                'Date': 'сегмент',
                'Device': 'сегмент',
                'DynamicTextAdTargetId': '–',
                'ExternalNetworkName': 'сегмент',
                'Gender': 'сегмент',
                'GoalsRoi': 'метрика',
                'ImpressionReach': '–',
                'Impressions': 'метрика',
                'ImpressionShare': '–',
                'IncomeGrade': 'сегмент',
                'Keyword': '–',
                'LocationOfPresenceId': 'сегмент',
                'LocationOfPresenceName': 'сегмент',
                'MatchedKeyword': '–',
                'MatchType': 'сегмент',
                'MobilePlatform': 'сегмент',
                'Month': 'сегмент',
                'Placement': 'сегмент',
                'Profit': 'метрика',
                'Quarter': 'сегмент',
                'Query': '–',
                'Revenue': 'метрика',
                'RlAdjustmentId': '–',
                'Sessions': 'метрика',
                'Slot': 'сегмент',
                'SmartAdTargetId': '–',
                'TargetingCategory': 'сегмент',
                'TargetingLocationId': 'сегмент',
                'TargetingLocationName': 'сегмент',
                'Week': 'сегмент',
                'WeightedCtr': 'метрика',
                'WeightedImpressions': 'метрика',
                'Year': 'сегмент',
            },
        'AD_PERFORMANCE_REPORT':
            {
                'AdFormat': 'сегмент',
                'AdGroupId': 'атрибут',
                'AdGroupName': 'атрибут',
                'AdId': 'атрибут',
                'AdNetworkType': 'сегмент',
                'Age': 'сегмент',
                'AudienceTargetId': '–',
                'AvgClickPosition': 'метрика',
                'AvgCpc': 'метрика',
                'AvgCpm': '–',
                'AvgEffectiveBid': 'метрика',
                'AvgImpressionFrequency': '–',
                'AvgImpressionPosition': 'метрика',
                'AvgPageviews': 'метрика',
                'AvgTrafficVolume': 'метрика',
                'BounceRate': 'метрика',
                'Bounces': 'метрика',
                'CampaignId': 'атрибут',
                'CampaignName': 'атрибут',
                'CampaignUrlPath': 'атрибут',
                'CampaignType': 'атрибут',
                'CarrierType': 'сегмент',
                'Clicks': 'метрика',
                'ClickType': 'сегмент',
                'ClientLogin': 'сегмент',
                'ConversionRate': 'метрика',
                'Conversions': 'метрика',
                'Cost': 'метрика',
                'CostPerConversion': 'метрика',
                'Criterion': '–',
                'CriterionId': '–',
                'CriterionType': 'сегмент',
                'Ctr': 'метрика',
                'Date': 'сегмент',
                'Device': 'сегмент',
                'DynamicTextAdTargetId': '–',
                'ExternalNetworkName': 'сегмент',
                'Gender': 'сегмент',
                'GoalsRoi': 'метрика',
                'ImpressionReach': '–',
                'Impressions': 'метрика',
                'ImpressionShare': '–',
                'IncomeGrade': 'сегмент',
                'Keyword': '–',
                'LocationOfPresenceId': 'сегмент',
                'LocationOfPresenceName': 'сегмент',
                'MatchedKeyword': '–',
                'MatchType': 'сегмент',
                'MobilePlatform': 'сегмент',
                'Month': 'сегмент',
                'Placement': 'сегмент',
                'Profit': 'метрика',
                'Quarter': 'сегмент',
                'Query': '–',
                'Revenue': 'метрика',
                'RlAdjustmentId': '–',
                'Sessions': 'метрика',
                'Slot': 'сегмент',
                'SmartAdTargetId': '–',
                'TargetingCategory': 'сегмент',
                'TargetingLocationId': 'сегмент',
                'TargetingLocationName': 'сегмент',
                'Week': 'сегмент',
                'WeightedCtr': 'метрика',
                'WeightedImpressions': 'метрика',
                'Year': 'сегмент',
            },
        'ADGROUP_PERFORMANCE_REPORT':
            {
                'AdFormat': 'сегмент',
                'AdGroupId': 'атрибут',
                'AdGroupName': 'атрибут',
                'AdId': '–',
                'AdNetworkType': 'сегмент',
                'Age': 'сегмент',
                'AudienceTargetId': '–',
                'AvgClickPosition': 'метрика',
                'AvgCpc': 'метрика',
                'AvgCpm': '–',
                'AvgEffectiveBid': 'метрика',
                'AvgImpressionFrequency': '–',
                'AvgImpressionPosition': 'метрика',
                'AvgPageviews': 'метрика',
                'AvgTrafficVolume': 'метрика',
                'BounceRate': 'метрика',
                'Bounces': 'метрика',
                'CampaignId': 'атрибут',
                'CampaignName': 'атрибут',
                'CampaignUrlPath': 'атрибут',
                'CampaignType': 'атрибут',
                'CarrierType': 'сегмент',
                'Clicks': 'метрика',
                'ClickType': 'сегмент',
                'ClientLogin': 'сегмент',
                'ConversionRate': 'метрика',
                'Conversions': 'метрика',
                'Cost': 'метрика',
                'CostPerConversion': 'метрика',
                'Criterion': '–',
                'CriterionId': '–',
                'CriterionType': 'сегмент',
                'Ctr': 'метрика',
                'Date': 'сегмент',
                'Device': 'сегмент',
                'DynamicTextAdTargetId': '–',
                'ExternalNetworkName': 'сегмент',
                'Gender': 'сегмент',
                'GoalsRoi': 'метрика',
                'ImpressionReach': '–',
                'Impressions': 'метрика',
                'ImpressionShare': 'метрика',
                'IncomeGrade': 'сегмент',
                'Keyword': '–',
                'LocationOfPresenceId': 'сегмент',
                'LocationOfPresenceName': 'сегмент',
                'MatchedKeyword': '–',
                'MatchType': 'сегмент',
                'MobilePlatform': 'сегмент',
                'Month': 'сегмент',
                'Placement': 'сегмент',
                'Profit': 'метрика',
                'Quarter': 'сегмент',
                'Query': '–',
                'Revenue': 'метрика',
                'RlAdjustmentId': '–',
                'Sessions': 'метрика',
                'Slot': 'сегмент',
                'SmartAdTargetId': '–',
                'TargetingCategory': 'сегмент',
                'TargetingLocationId': 'сегмент',
                'TargetingLocationName': 'сегмент',
                'Week': 'сегмент',
                'WeightedCtr': 'метрика',
                'WeightedImpressions': 'метрика',
                'Year': 'сегмент',
            },
        'CAMPAIGN_PERFORMANCE_REPORT':
            {
                'AdFormat': 'сегмент',
                'AdGroupId': '–',
                'AdGroupName': '–',
                'AdId': '–',
                'AdNetworkType': 'сегмент',
                'Age': 'сегмент',
                'AudienceTargetId': '–',
                'AvgClickPosition': 'метрика',
                'AvgCpc': 'метрика',
                'AvgCpm': '–',
                'AvgEffectiveBid': 'метрика',
                'AvgImpressionFrequency': '–',
                'AvgImpressionPosition': 'метрика',
                'AvgPageviews': 'метрика',
                'AvgTrafficVolume': 'метрика',
                'BounceRate': 'метрика',
                'Bounces': 'метрика',
                'CampaignId': 'атрибут',
                'CampaignName': 'атрибут',
                'CampaignUrlPath': 'атрибут',
                'CampaignType': 'атрибут',
                'CarrierType': 'сегмент',
                'Clicks': 'метрика',
                'ClickType': 'сегмент',
                'ClientLogin': 'сегмент',
                'ConversionRate': 'метрика',
                'Conversions': 'метрика',
                'Cost': 'метрика',
                'CostPerConversion': 'метрика',
                'Criterion': '–',
                'CriterionId': '–',
                'CriterionType': 'сегмент',
                'Ctr': 'метрика',
                'Date': 'сегмент',
                'Device': 'сегмент',
                'DynamicTextAdTargetId': '–',
                'ExternalNetworkName': 'сегмент',
                'Gender': 'сегмент',
                'GoalsRoi': 'метрика',
                'ImpressionReach': '–',
                'Impressions': 'метрика',
                'ImpressionShare': 'метрика',
                'IncomeGrade': 'сегмент',
                'Keyword': '–',
                'LocationOfPresenceId': 'сегмент',
                'LocationOfPresenceName': 'сегмент',
                'MatchedKeyword': '–',
                'MatchType': 'сегмент',
                'MobilePlatform': 'сегмент',
                'Month': 'сегмент',
                'Placement': 'сегмент',
                'Profit': 'метрика',
                'Quarter': 'сегмент',
                'Query': '–',
                'Revenue': 'метрика',
                'RlAdjustmentId': '–',
                'Sessions': 'метрика',
                'Slot': 'сегмент',
                'SmartAdTargetId': '–',
                'TargetingCategory': 'сегмент',
                'TargetingLocationId': 'сегмент',
                'TargetingLocationName': 'сегмент',
                'Week': 'сегмент',
                'WeightedCtr': 'метрика',
                'WeightedImpressions': 'метрика',
                'Year': 'сегмент',
            },
        'CRITERIA_PERFORMANCE_REPORT':
            {
                'AdFormat': '–',
                'AdGroupId': 'атрибут',
                'AdGroupName': 'атрибут',
                'AdId': '–',
                'AdNetworkType': 'сегмент',
                'Age': 'сегмент',
                'AudienceTargetId': 'фильтр',
                'AvgClickPosition': 'метрика',
                'AvgCpc': 'метрика',
                'AvgCpm': '–',
                'AvgEffectiveBid': 'метрика',
                'AvgImpressionFrequency': '–',
                'AvgImpressionPosition': 'метрика',
                'AvgPageviews': 'метрика',
                'AvgTrafficVolume': 'метрика',
                'BounceRate': 'метрика',
                'Bounces': 'метрика',
                'CampaignId': 'атрибут',
                'CampaignName': 'атрибут',
                'CampaignUrlPath': 'атрибут',
                'CampaignType': 'атрибут',
                'CarrierType': 'сегмент',
                'Clicks': 'метрика',
                'ClickType': 'сегмент',
                'ClientLogin': 'сегмент',
                'ConversionRate': 'метрика',
                'Conversions': 'метрика',
                'Cost': 'метрика',
                'CostPerConversion': 'метрика',
                'Criterion': 'атрибут',
                'CriterionId': 'атрибут',
                'CriterionType': 'атрибут',
                'Ctr': 'метрика',
                'Date': 'сегмент',
                'Device': 'сегмент',
                'DynamicTextAdTargetId': 'фильтр',
                'ExternalNetworkName': 'сегмент',
                'Gender': 'сегмент',
                'GoalsRoi': 'метрика',
                'ImpressionReach': '–',
                'Impressions': 'метрика',
                'ImpressionShare': 'метрика',
                'IncomeGrade': 'сегмент',
                'Keyword': 'фильтр',
                'LocationOfPresenceId': 'сегмент',
                'LocationOfPresenceName': 'сегмент',
                'MatchedKeyword': '–',
                'MatchType': 'сегмент',
                'MobilePlatform': 'сегмент',
                'Month': 'сегмент',
                'Placement': 'сегмент',
                'Profit': 'метрика',
                'Quarter': 'сегмент',
                'Query': '–',
                'Revenue': 'метрика',
                'RlAdjustmentId': 'сегмент',
                'Sessions': 'метрика',
                'Slot': 'сегмент',
                'SmartAdTargetId': 'фильтр',
                'TargetingCategory': 'сегмент',
                'TargetingLocationId': 'сегмент',
                'TargetingLocationName': 'сегмент',
                'Week': 'сегмент',
                'WeightedCtr': 'метрика',
                'WeightedImpressions': 'метрика',
                'Year': 'сегмент',
            },
        'CUSTOM_REPORT':
            {
                'AdFormat': 'сегмент',
                'AdGroupId': 'сегмент',
                'AdGroupName': 'сегмент',
                'AdId': 'сегмент',
                'AdNetworkType': 'сегмент',
                'Age': 'сегмент',
                'AudienceTargetId': 'фильтр',
                'AvgClickPosition': 'метрика',
                'AvgCpc': 'метрика',
                'AvgCpm': '–',
                'AvgEffectiveBid': 'метрика',
                'AvgImpressionFrequency': '–',
                'AvgImpressionPosition': 'метрика',
                'AvgPageviews': 'метрика',
                'AvgTrafficVolume': 'метрика',
                'BounceRate': 'метрика',
                'Bounces': 'метрика',
                'CampaignId': 'сегмент',
                'CampaignName': 'сегмент',
                'CampaignUrlPath': 'сегмент',
                'CampaignType': 'сегмент',
                'CarrierType': 'сегмент',
                'Clicks': 'метрика',
                'ClickType': 'сегмент',
                'ClientLogin': 'сегмент',
                'ConversionRate': 'метрика',
                'Conversions': 'метрика',
                'Cost': 'метрика',
                'CostPerConversion': 'метрика',
                'Criterion': 'сегмент',
                'CriterionId': 'сегмент',
                'CriterionType': 'сегмент',
                'Ctr': 'метрика',
                'Date': 'сегмент',
                'Device': 'сегмент',
                'DynamicTextAdTargetId': 'фильтр',
                'ExternalNetworkName': 'сегмент',
                'Gender': 'сегмент',
                'GoalsRoi': 'метрика',
                'ImpressionReach': '–',
                'Impressions': 'метрика',
                'ImpressionShare': '–',
                'IncomeGrade': 'сегмент',
                'Keyword': 'фильтр',
                'LocationOfPresenceId': 'сегмент',
                'LocationOfPresenceName': 'сегмент',
                'MatchedKeyword': '–',
                'MatchType': 'сегмент',
                'MobilePlatform': 'сегмент',
                'Month': 'сегмент',
                'Placement': 'сегмент',
                'Profit': 'метрика',
                'Quarter': 'сегмент',
                'Query': '–',
                'Revenue': 'метрика',
                'RlAdjustmentId': 'сегмент',
                'Sessions': 'метрика',
                'Slot': 'сегмент',
                'SmartAdTargetId': 'фильтр',
                'TargetingCategory': 'сегмент',
                'TargetingLocationId': 'сегмент',
                'TargetingLocationName': 'сегмент',
                'Week': 'сегмент',
                'WeightedCtr': 'метрика',
                'WeightedImpressions': 'метрика',
                'Year': 'сегмент',
            },
        'REACH_AND_FREQUENCY_PERFORMANCE_REPORT':
            {
                'AdFormat': '–',
                'AdGroupId': 'сегмент',
                'AdGroupName': 'сегмент',
                'AdId': 'сегмент',
                'AdNetworkType': '–',
                'Age': 'сегмент',
                'AudienceTargetId': '–',
                'AvgClickPosition': '–',
                'AvgCpc': 'метрика',
                'AvgCpm': 'метрика',
                'AvgEffectiveBid': 'метрика',
                'AvgImpressionFrequency': 'метрика',
                'AvgImpressionPosition': '–',
                'AvgPageviews': 'метрика',
                'AvgTrafficVolume': 'метрика',
                'BounceRate': 'метрика',
                'Bounces': 'метрика',
                'CampaignId': 'сегмент',
                'CampaignName': 'сегмент',
                'CampaignUrlPath': 'сегмент',
                'CampaignType': 'сегмент',
                'CarrierType': '–',
                'Clicks': 'метрика',
                'ClickType': '–',
                'ClientLogin': 'сегмент',
                'ConversionRate': 'метрика',
                'Conversions': 'метрика',
                'Cost': 'метрика',
                'CostPerConversion': 'метрика',
                'Criterion': '–',
                'CriterionId': '–',
                'CriterionType': '–',
                'Ctr': 'метрика',
                'Date': 'сегмент',
                'Device': 'сегмент',
                'DynamicTextAdTargetId': '–',
                'ExternalNetworkName': '–',
                'Gender': 'сегмент',
                'GoalsRoi': 'метрика',
                'ImpressionReach': 'метрика',
                'Impressions': 'метрика',
                'ImpressionShare': '–',
                'IncomeGrade': '–',
                'Keyword': '–',
                'LocationOfPresenceId': '–',
                'LocationOfPresenceName': '–',
                'MatchedKeyword': '–',
                'MatchType': '–',
                'MobilePlatform': '–',
                'Month': 'сегмент',
                'Placement': '–',
                'Profit': 'метрика',
                'Quarter': 'сегмент',
                'Query': '–',
                'Revenue': 'метрика',
                'RlAdjustmentId': '–',
                'Sessions': 'метрика',
                'Slot': '–',
                'SmartAdTargetId': '–',
                'TargetingCategory': '–',
                'TargetingLocationId': 'сегмент',
                'TargetingLocationName': 'сегмент',
                'Week': 'сегмент',
                'WeightedCtr': 'метрика',
                'WeightedImpressions': 'метрика',
                'Year': 'сегмент',
            },
        'SEARCH_QUERY_PERFORMANCE_REPORT':
            {
                'AdFormat': '–',
                'AdGroupId': 'атрибут',
                'AdGroupName': 'атрибут',
                'AdId': 'сегмент',
                'AdNetworkType': '–',
                'Age': '–',
                'AudienceTargetId': '–',
                'AvgClickPosition': 'метрика',
                'AvgCpc': 'метрика',
                'AvgCpm': '–',
                'AvgEffectiveBid': 'метрика',
                'AvgImpressionFrequency': '–',
                'AvgImpressionPosition': 'метрика',
                'AvgPageviews': 'метрика',
                'AvgTrafficVolume': 'метрика',
                'BounceRate': 'метрика',
                'Bounces': 'метрика',
                'CampaignId': 'атрибут',
                'CampaignName': 'атрибут',
                'CampaignUrlPath': 'атрибут',
                'CampaignType': 'атрибут',
                'CarrierType': '–',
                'Clicks': 'метрика',
                'ClickType': '–',
                'ClientLogin': 'сегмент',
                'ConversionRate': 'метрика',
                'Conversions': 'метрика',
                'Cost': 'метрика',
                'CostPerConversion': 'метрика',
                'Criterion': 'сегмент',
                'CriterionId': 'сегмент',
                'CriterionType': 'сегмент',
                'Ctr': 'метрика',
                'Date': 'сегмент',
                'Device': '–',
                'DynamicTextAdTargetId': 'фильтр',
                'ExternalNetworkName': '–',
                'Gender': '–',
                'GoalsRoi': 'метрика',
                'ImpressionReach': '–',
                'Impressions': 'метрика',
                'ImpressionShare': '–',
                'IncomeGrade': 'сегмент',
                'Keyword': 'фильтр',
                'LocationOfPresenceId': '–',
                'LocationOfPresenceName': '–',
                'MatchedKeyword': 'сегмент',
                'MatchType': 'сегмент',
                'MobilePlatform': '–',
                'Month': 'сегмент',
                'Placement': 'сегмент',
                'Profit': 'метрика',
                'Quarter': 'сегмент',
                'Query': 'атрибут',
                'Revenue': 'метрика',
                'RlAdjustmentId': '–',
                'Sessions': '–',
                'Slot': '–',
                'SmartAdTargetId': '–',
                'TargetingCategory': 'сегмент',
                'TargetingLocationId': '–',
                'TargetingLocationName': '–',
                'Week': 'сегмент',
                'WeightedCtr': 'метрика',
                'WeightedImpressions': 'метрика',
                'Year': 'сегмент',
            }
    }
