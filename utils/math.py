from config import DISCOUNT_PERCENT, COMMISSION_PERCENT


def multiplier_percent(percent: int) -> float:
    return 100/(100-percent)


def commission_price(money: int) -> int:
    res = money * multiplier_percent(COMMISSION_PERCENT)
    return round(res) if round(res) == res else int(res)+1


def pure_price(money: int) -> int:
    res = money / multiplier_percent(COMMISSION_PERCENT)
    return round(res) if round(res) == res else int(res)


def discount_price(money: int) -> int:
    res = round(money / multiplier_percent(DISCOUNT_PERCENT))
    return round(res) if round(res) == res else int(res)+1


if __name__ == '__main__':
    print(commission_price(200))
    print(pure_price(223))
    print(discount_price(100))
