def remove_lesser(array: list, value, is_including=False):
    result, index = array.copy(), -1
    if len(result):
        indices = [i for i, v in enumerate(result) if v < value]
        if indices:
            index = max(indices)
            index += 2 if is_including else 1
            del result[:index]
    return result, index


def remove_greater(array: list, value, is_including=False):
    result, index = array.copy(), -1
    if len(result):
        indices = [i for i, v in enumerate(result) if v > value]
        if indices:
            index = min(indices)
            index -= 1 if is_including else 0
            del result[index:]
    return result, index


def split_to_subarrays(array: list, elements_count: int, with_reminder=False):
    result = []
    subarrays_count = len(array) // elements_count
    if with_reminder and len(array) % elements_count:
        subarrays_count += 1
    for i in range(subarrays_count):
        start = i * elements_count
        stop = start + elements_count
        result.append(array[start: stop])
    return result
