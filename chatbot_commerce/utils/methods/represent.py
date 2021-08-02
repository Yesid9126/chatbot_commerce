def im_int(value):
    try:
        int(value)
        return True
    except ValueError:
        return False


def im_bool(value):
    value = value.strip().capitalize()
    if value in ['True', 'False']:
        return True
    return False


def im_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def im_from(value):
    if im_int(value):
        return int(value)
    if im_float(value):
        return float(value)
    if im_bool(value):
        return value.strip().capitalize() == 'True'
    return value


def parser_to_represent(array_string_splited):
    return [im_from(value) for value in array_string_splited]
# ", ".join(allowed_keys)
