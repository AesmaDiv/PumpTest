"""
    Модуль вспомогательных функций для всякий операций
"""
from collections import defaultdict
from itertools import chain
from operator import methodcaller


def safe_parse_to(to_type: type, string: str, default=None):
    """ Безопасная конвертация типов """
    try:
        return to_type(string)
    except (ValueError, TypeError):
        return default


def safe_parse_to_float(string: str):
    """ Безопасная конвертация строки в число с пл.запятой """
    return safe_parse_to(float, string, default=0.0)


def merge_dictionaries(list_of_dicts: list):
    """ Объединение списка словарей """
    dd = defaultdict(list)
    dict_items = map(methodcaller('items'), list_of_dicts)
    for k, v in chain.from_iterable(dict_items):
        dd[k].append(v)
    return dd


def remove_lesser(array: list, value, is_including=False):
    """ Удаление из списка значений МЕНЬШЕ чем 'value'
        'is_including' - включительно
        возвращает новый список и новую длину
    """
    result, index = array.copy(), -1
    if result:
        indices = [i for i, v in enumerate(result) if v < value]
        if indices:
            index = max(indices)
            index += 2 if is_including else 1
            del result[:index]
    return result, index


def remove_greater(array: list, value, is_including=False):
    """ Удаление из списка значений БОЛЬШЕ чем 'value'
        'is_including' - включительно
        возвращает новый список и новую длину
    """
    result, index = array.copy(), -1
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
