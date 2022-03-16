def convert(l : list):
    s = ''
    for i in l:
        if type(i) == list:
            for j in i:
                s += str(j) + ' '
            s += '\n'
            continue
        s += str(i) + '\n'
    return s
