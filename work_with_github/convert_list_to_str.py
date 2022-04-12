def convert(ls: list):
    s = ''
    for i in ls:
        if type(i) == list:
            for j in i:
                s += str(j) + ' '
            s += '\n'
            continue
        s += str(i) + ' '
    return s
