from datetime import datetime
import datetime as date_time


def datetime_per_day(dt_l: datetime, dt_r: datetime):
    tz = date_time.timezone.utc
    if dt_l.day < dt_r.day or dt_l.year < dt_r.year or dt_l.month < dt_r.month:
        return datetime(dt_l.year, dt_l.month, dt_l.day, 23, 59, 59, 0, tzinfo=tz)
    else:
        return dt_r


def datetime_begin_of_day(dt: datetime):
    tz = date_time.timezone.utc
    return datetime(dt.year, dt.month, dt.day, 0, 0, 0, 0, tzinfo=tz)
