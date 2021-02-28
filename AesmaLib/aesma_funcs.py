"""
    Модуль вспомогательных функций для всякий операций
"""

def safe_parse_to(to_type: type, string: str, default=None):
    """ Безопасная конвертация типов """
    try:
        return to_type(string)
    except (ValueError, TypeError):
        return default


def safe_parse_to_float(string: str):
    """ Безопасная конвертация строки в число с пл.запятой """
    return safe_parse_to(float, string, default=0.0)


def combine_dicts(list_of_dicts: list):
    """ Объединение списка словарей """
    if list_of_dicts:
        if len(list_of_dicts) == 1:
            return list_of_dicts[0]
        if isinstance(list_of_dicts[0], dict):
            list_of_keys = list(list_of_dicts[0].keys())
            list_of_vals = [list(d.values()) for d in list_of_dicts]
            result = dict(zip(list_of_keys, list_of_vals))
            return dict(result)
    return dict()


def remove_lesser(sorted_array: list, value, is_including=False):
    """ Удаляет из упорядоченого списка значения МЕНЬШЕ чем 'value'
        'is_including' - включительно
        возвращает новый список и индекс первого елемента
        соответствующего условию
    """
    result, index = sorted_array.copy(), -1
    if result:
        indices = [i for i, v in enumerate(result) if v < value]
        if indices:
            index = max(indices)
            index += 2 if is_including else 1
            del result[:index]
    return result, index


def remove_greater(sorted_array: list, value, is_including=False):
    """ Удаляет из упорядоченого списка значения БОЛЬШЕ чем 'value'
        'is_including' - включительно
        возвращает новый список и индекс последнего елемента
        соответствующего условию
    """
    result, index = sorted_array.copy(), -1
    if result:
        indices = [i for i, v in enumerate(result) if v > value]
        if indices:
            index = min(indices)
            index -= 1 if is_including else 0
            del result[index:]
    return result, index


def split_to_subarrays(array: list, elements_count: int, with_reminder=False):
    """ Разбивает список на части по 'elements_count' частей
        'with_reminder' - с остатком
    """
    result = []
    subarrays_count = len(array) // elements_count
    if with_reminder and len(array) % elements_count:
        subarrays_count += 1
    for i in range(subarrays_count):
        start = i * elements_count
        stop = start + elements_count
        result.append(array[start: stop])
    return result
