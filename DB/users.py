import json
from typing import List

from DB import DB

from profile_api import get_profile, get_books


def check_users():

    QUERY = 'SELECT id_vk, profile_key FROM users WHERE profile_key IS NOT NULL AND is_active=TRUE;'

    res = DB().query(QUERY)

    for i in res:
        inv = [int(data) for data in get_profile(i[1], i[0])['items']]
        class_id = inv[0] if inv[0] != 14108 else inv[1]
        build = get_books(inv)

        update_user(i[0], equipment=json.dumps(build), class_id=class_id)

    return


def add_user(id_vk: int, profile_key: (str, None), is_active: bool, is_leader: bool, is_officer: bool, equipment: (str, None), class_id: (str, None)):

    QUERY = 'INSERT INTO `users` VALUE ( %s, %s, %s, %s, %s, %s, %s );'

    try:
        id_vk = int(id_vk)
    except ValueError:
        raise TypeError(f"`id_vk` must be int, got {id_vk} instead")

    if class_id:
        try:
            class_id = int(class_id)
        except ValueError:
            raise TypeError(f"`class_id` must be int, got {class_id} instead")

    data = (id_vk, profile_key if profile_key else None, is_active, is_leader, is_officer, equipment if equipment else None, class_id if class_id else None)

    DB().query(QUERY, data)
    return


def update_user(id_vk: int, **kwargs):
    QUERY = 'UPDATE `users` SET ' + ', '.join([k + ' = %s' for k in kwargs.keys()]) + ' WHERE id_vk = %s;'

    try:
        id_vk = int(id_vk)
    except ValueError:
        raise TypeError(f"`id_vk` must be int, got {id_vk} instead")

    data = tuple(kwargs.values())

    DB().query(QUERY, (*data, id_vk))
    return


def get_user(id_vk: int) -> (dict, None):
    QUERY = 'SELECT id_vk, profile_key, is_active, is_leader, is_officer, equipment, class_id, balance FROM users WHERE id_vk = %s;'

    try:
        id_vk = int(id_vk)
    except ValueError:
        raise TypeError(f"`id_vk` must be int, got {id_vk} instead")

    res = DB().query(QUERY, (id_vk,))

    if res:
        res = res[0]
        return {'id_vk': res[0], 'profile_key': res[1], 'is_active': res[2], 'is_leader': res[3], 'is_officer': res[4],
                'equipment': res[5], 'class_id': res[6], 'balance': res[7]}
    else:
        return


def get_equip():
    QUERY = 'SELECT id_vk, equipment FROM users WHERE equipment IS NOT NULL AND is_active=TRUE;'
    res = DB().query(QUERY)
    answer = []
    for row in res:
        answer.append((row[0], json.loads(row[1])))

    return answer


def get_leaders() -> tuple:
    QUERY = 'SELECT id_vk FROM users WHERE is_leader = 1;'
    res = DB().query(QUERY)
    answer = [row[0] for row in res]

    return tuple(answer)


def check_active(members: List[int]) -> None:

    # SET all users as inactive

    DB().query('UPDATE users SET is_active=FALSE;')

    # Set all users from list as active

    for u in members:
        if get_user(u):
            update_user(u, is_active=True)

    # Revoke roles if inactive

    DB().query('UPDATE users SET is_officer=FALSE, is_leader=FALSE WHERE is_active=FALSE;')

    return


def get_balance(id_vk: int):

    try:
        id_vk = int(id_vk)
    except ValueError:
        raise TypeError(f"`id_vk` must be int, got {id_vk} instead")

    res = DB().query('SELECT balance FROM users WHERE is_active = 1 AND id_vk = %s;', (id_vk,))
    if res:
        return res[0][0]
    else:
        return


def change_balance(id_vk: int, amount: int) -> (int, None):

    try:
        id_vk = int(id_vk)
    except ValueError:
        raise TypeError(f"`id_vk` must be int, got {id_vk} instead")

    try:
        amount = int(amount)
    except ValueError:
        raise TypeError(f"`amount` must be int, got {amount} instead")

    balance = get_balance(id_vk)
    if balance is None:
        return

    DB().query('UPDATE users SET balance = %s WHERE id_vk = %s;', (balance+amount, id_vk))

    return balance+amount


if __name__ == '__main__':
    # print(change_balance(158154503, -1000))
    # add_user(3934797, None, True, False, False, None, None)
    # update_user(3934797, is_active=False)
    # print(get_equip())
    pass
