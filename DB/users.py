import json
from typing import List

from DB.instance import DB
import mysql.connector.errors as sql_err

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

    db = DB().query(QUERY, data)
    return


def update_user(id_vk: int, **kwargs):
    QUERY = 'UPDATE `users` SET ' + ', '.join([k + ' = %s' for k in kwargs.keys()]) + ' WHERE id_vk = %s;'

    try:
        id_vk = int(id_vk)
    except ValueError:
        raise TypeError(f"`id_vk` must be int, got {id_vk} instead")

    data = tuple(kwargs.values())

    db = DB().query(QUERY, (*data, id_vk))
    return


def get_user(id_vk: int) -> (dict, None):
    QUERY = 'SELECT id_vk, profile_key, is_active, is_leader, is_officer, equipment, class_id FROM users WHERE id_vk = %s;'

    try:
        id_vk = int(id_vk)
    except ValueError:
        raise TypeError(f"`id_vk` must be int, got {id_vk} instead")

    res = DB().query(QUERY, (id_vk,))

    if res:
        return {'id_vk': res[0], 'profile_key': res[1], 'is_active': res[2], 'is_leader': res[3], 'is_officer': res[4],
                'equipment': res[5], 'class_id': res[6]}
    else:
        return


def get_equip():
    QUERY = 'SELECT id_vk, equipment FROM users WHERE equipment IS NOT NULL AND is_active=TRUE;'
    db = DB().connect()
    cur = db.cursor()
    try:
        cur.execute(QUERY)
        res = cur.fetchall()
    except sql_err.ProgrammingError as exc:
        raise ValueError(exc.msg)
    finally:
        cur.close()
        db.close()
    answer = []
    for row in res:
        answer.append((row[0], json.loads(row[1])))

    return answer


def get_leaders() -> tuple:
    # TODO: make query
    return tuple([205486328, 16914430, 158154503])


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


if __name__ == '__main__':
    # add_user(3934797, None, True, False, False, None, None)
    # update_user(3934797, is_active=False)
    print(get_equip())
