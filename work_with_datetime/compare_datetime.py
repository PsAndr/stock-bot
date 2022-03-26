from datetime import datetime


def compare(dt1: datetime, dt2: datetime):
    #print(f'compare: {dt1}, {dt2}')
    if dt1.year > dt2.year:
        return True
    elif dt1.year < dt2.year:
        return False
    if dt1.month > dt2.month:
        return True
    elif dt1.month < dt2.month:
        return False
    if dt1.day > dt2.day:
        return True
    elif dt1.day < dt2.day:
        return False
    if dt1.hour > dt2.hour:
        return True
    elif dt1.hour < dt2.hour:
        return False
    if dt1.minute > dt2.minute:
        return True
    elif dt1.minute < dt2.minute:
        return False
    if dt1.second >= dt2.second:
        return True
    return False
