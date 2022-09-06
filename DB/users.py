import json

from DB.instance import DB
import mysql.connector.errors as sql_err

from profile_api import get_profile, get_books


def check_users():
    QUERY = 'SELECT id_vk, profile_key FROM users WHERE profile_key IS NOT NULL;'
    # TODO: update build and class_id

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

    for i in res:
        inv = [int(i) for i in get_profile(i[1], i[0])['items']]
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

    db = DB().connect()
    cur = db.cursor()
    try:
        cur.execute(QUERY, data)
        db.commit()
    except sql_err.IntegrityError as exc:
        db.rollback()
        raise KeyError(exc.msg)
    finally:
        cur.close()
        db.close()

    return


def update_user(id_vk: int, **kwargs):
    QUERY = 'UPDATE `users` SET ' + ', '.join([k + ' = %s' for k in kwargs.keys()]) + ' WHERE id_vk = %s;'

    try:
        id_vk = int(id_vk)
    except ValueError:
        raise TypeError(f"`id_vk` must be int, got {id_vk} instead")

    data = tuple(kwargs.values())

    db = DB().connect()
    cur = db.cursor()
    try:
        cur.execute(QUERY, (*data, id_vk))
        db.commit()
    except sql_err.ProgrammingError as exc:
        db.rollback()
        raise KeyError(exc.msg)
    finally:
        cur.close()
        db.close()


def get_user(id_vk: int):
    QUERY = 'SELECT id_vk, profile_key, is_active, is_leader, is_officer, equipment, class_id FROM users WHERE id_vk = %s;'

    try:
        id_vk = int(id_vk)
    except ValueError:
        raise TypeError(f"`id_vk` must be int, got {id_vk} instead")

    db = DB().connect()
    cur = db.cursor()
    try:
        cur.execute(QUERY, (id_vk,))
        res = cur.fetchone()
    except sql_err.ProgrammingError as exc:
        raise ValueError(exc.msg)
    finally:
        cur.close()
        db.close()

    if res:
        return {'id_vk': res[0], 'profile_key': res[1], 'is_active': res[2], 'is_leader': res[3], 'is_officer': res[4], 'equipment': res[5],
                'class_id': res[6]}
    else:
        return


def get_equip():
    QUERY = 'SELECT id_vk, equipment FROM users WHERE equipment IS NOT NULL;'
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


if __name__ == '__main__':
    # add_user(3934797, None, True, False, False, None, None)
    # update_user(3934797, is_active=False)
    print(get_equip())



