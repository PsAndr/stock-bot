from datetime import datetime


def get(dt: datetime, dt2: datetime):
    to_return = dict()
    to_return['year'] = dt.year - dt2.year
    to_return['month'] = dt.month - dt2.month
    to_return['day'] = dt.day - dt2.day
    to_return['hour'] = dt.hour - dt2.hour
    to_return['minute'] = dt.minute - dt2.minute
    to_return['second'] = dt.second - dt2.second
    to_return['microsecond'] = dt.microsecond - dt2.microsecond
    return to_return
