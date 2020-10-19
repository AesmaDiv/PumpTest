from collections import defaultdict
from itertools import chain
from operator import methodcaller


def safe_parse_to(to_type: type, string: str, default=None):
    try:
        return to_type(string)
    except (ValueError, TypeError):
        return default


def safe_parse_to_float(string: str):
    return safe_parse_to(float, string, default=0.0)


def convert_flow(flowmeter: int):
    return flowmeter


def merge_dictionaries(list_of_dicts: list):
    dd = defaultdict(list)
    dict_items = map(methodcaller('items'), list_of_dicts)
    for k, v in chain.from_iterable(dict_items):
        dd[k].append(v)
    return dd
