import datetime

def convert(dt : datetime):
    return str(dt).replace('-', ' ').replace(':', ' ').split()