from datetime import datetime


def str_datetime(d: datetime) -> str:
    return '{:0>2}'.format(d.day) + '.' + '{:0>2}'.format(d.month) + '.' + '{:0>2}'.format(d.year % 100) + ' ' + \
           '{:0>2}'.format(d.hour) + ':' + '{:0>2}'.format(d.minute)


def datediff(d1: datetime, d2: datetime) -> str:
    diff = max(d1, d2) - min(d1, d2)
    res = 'Прошло '
    if diff.days:
        res += str(diff.days)
        if diff.days // 10 == 1 or diff.days % 10 > 4:
            res += ' дней '
        elif diff.days % 10 > 1:
            res += ' дня '
        elif diff.days % 10 == 1:
            res += ' день '
    h = diff.seconds // 3600
    if h:
        res += str(h)
        if h // 10 == 1 or h % 10 > 4 or h % 10 == 0:
            res += ' часов '
        elif h % 10 > 1:
            res += ' часа '
        elif h % 10 == 1:
            res += ' час '
    # even if d1==d2, result will be not empty
    m = diff.seconds % 3600 // 60
    res += str(m)
    if m // 10 == 1 or m % 10 > 4 or m % 10 == 0:
        res += ' минут '
    elif m % 10 > 1:
        res += ' минуты '
    elif m % 10 == 1:
        res += ' минута '
    return res.strip()
