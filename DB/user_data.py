from datetime import datetime as dt
from DB.instance import DB
import mysql.connector.errors as sql_err


def add_user_data(id_vk: int, lvl: int, atk: int, defence: int, strength: int, agile: int, end: int, luck: int, acc: (int, None), conc: (int, None)):

    QUERY = 'INSERT INTO `user_data` VALUE ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s , %s );'

    try:
        id_vk = int(id_vk)
    except ValueError:
        raise TypeError(f"`id_vk` must be int, got {id_vk} instead")

    try:
        lvl = int(lvl)
    except ValueError:
        raise TypeError(f"`lvl` must be int, got {lvl} instead")

    try:
        atk = int(atk)
    except ValueError:
        raise TypeError(f"`atk` must be int, got {atk} instead")

    try:
        defence = int(defence)
    except ValueError:
        raise TypeError(f"`defence` must be int, got {defence} instead")

    try:
        strength = int(strength)
    except ValueError:
        raise TypeError(f"`strength` must be int, got {strength} instead")

    try:
        agile = int(agile)
    except ValueError:
        raise TypeError(f"`agile` must be int, got {agile} instead")

    try:
        end = int(end)
    except ValueError:
        raise TypeError(f"`end` must be int, got {end} instead")

    try:
        luck = int(luck)
    except ValueError:
        raise TypeError(f"`luck` must be int, got {luck} instead")

    if acc:
        try:
            acc = int(acc)
        except ValueError:
            raise TypeError(f"`acc` must be int, got {acc} instead")

    if conc:
        try:
            conc = int(conc)
        except ValueError:
            raise TypeError(f"`conc` must be int, got {conc} instead")

    data = (id_vk, lvl, atk, defence, strength, agile, end, luck, acc, conc, dt.now())

    DB().query(QUERY, data)

    return


def update_user_data(id_vk: int, lvl: int, atk: int, defence: int, strength: int, agile: int, end: int, luck: int, acc: (int, None), conc: (int, None)):

    QUERY = 'UPDATE `user_data` SET level = %s, attack = %s, defence = %s, strength = %s, agility = %s, endurance = %s, luck = %s, accuracy = %s, concentration = %s, last_update = %s WHERE id_vk = %s;'

    try:
        id_vk = int(id_vk)
    except ValueError:
        raise TypeError(f"`id_vk` must be int, got {id_vk} instead")

    try:
        lvl = int(lvl)
    except ValueError:
        raise TypeError(f"`lvl` must be int, got {lvl} instead")

    try:
        atk = int(atk)
    except ValueError:
        raise TypeError(f"`atk` must be int, got {atk} instead")

    try:
        defence = int(defence)
    except ValueError:
        raise TypeError(f"`defence` must be int, got {defence} instead")

    try:
        strength = int(strength)
    except ValueError:
        raise TypeError(f"`strength` must be int, got {strength} instead")

    try:
        agile = int(agile)
    except ValueError:
        raise TypeError(f"`agile` must be int, got {agile} instead")

    try:
        end = int(end)
    except ValueError:
        raise TypeError(f"`end` must be int, got {end} instead")

    try:
        luck = int(luck)
    except ValueError:
        raise TypeError(f"`luck` must be int, got {luck} instead")

    if acc:
        try:
            acc = int(acc)
        except ValueError:
            raise TypeError(f"`acc` must be int, got {acc} instead")

    if conc:
        try:
            conc = int(conc)
        except ValueError:
            raise TypeError(f"`conc` must be int, got {conc} instead")

    data = (lvl, atk, defence, strength, agile, end, luck, acc, conc, dt.now(), id_vk)

    DB().query(QUERY, data)

    return


def get_user_data(id_vk: int):

    QUERY = 'SELECT id_vk, `level`, attack, defence, strength, agility, endurance, luck, accuracy, concentration, last_update FROM user_data WHERE user_data.id_vk = %s;'

    try:
        id_vk = int(id_vk)
    except ValueError:
        raise TypeError(f"`id_vk` must be int, got {id_vk} instead")

    res = DB().query(QUERY, (id_vk,))

    if res:
        res = res[0]
        return {'id_vk': res[0], 'level': res[1], 'attack': res[2], 'defence': res[3], 'strength': res[4],
                'agility': res[5], 'endurance': res[6], 'luck': res[7], 'accuracy': res[8], 'concentration': res[9], 'last_update': res[10]}
    else:
        return


if __name__ == '__main__':
    # add_user_data(123141, 90, 120, 55, 123, 122, 129, 10, None, None)
    # update_user_data(123141, 90, 120, 55, 123, 122, 129, 10, 15, 45)
    print(get_user_data(3902377))

