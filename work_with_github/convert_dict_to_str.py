def convert(dct: dict):
    str_to_return = ''
    for key in dct:
        str_to_return += '{0}: {1}'.format(key, dct[key]) + '\n'
    return str_to_return
    