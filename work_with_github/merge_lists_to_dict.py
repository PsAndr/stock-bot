def merge(name: list, values: list):
    dc = dict()
    for ind, nm in enumerate(name):
        dc[nm] = values[ind]
    return dc
