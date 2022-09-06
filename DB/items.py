from DB.instance import DB
import mysql.connector.errors as sql_err
import json
import os


def check_items():
    QUERY = 'INSERT INTO `items` VALUES (%s, %s);'
    items = json.loads(open(os.environ.get('ITEM_FILE'), 'r').read())

    db = DB().connect()
    cur = db.cursor()
    for i in items:
        data = (i, items[i])
        try:
            cur.execute(QUERY, data)
            db.commit()
            # print(f'Added item {i}')
        except sql_err.IntegrityError as exc:
            db.rollback()
    cur.close()
    db.close()
    return


def get_item_by_id(item_id: int):
    QUERY = 'SELECT item_name FROM items WHERE item_id = %s;'

    try:
        item_id = int(item_id)
    except ValueError:
        raise TypeError(f"`item_id` must be int, got {item_id} instead")

    db = DB().connect()
    cur = db.cursor()
    try:
        cur.execute(QUERY, (item_id,))
        res = cur.fetchone()
    except sql_err.ProgrammingError as exc:
        raise ValueError(exc.msg)
    finally:
        cur.close()
        db.close()

    if res:
        return res[0]
    else:
        return


def get_item_by_name(name: str):
    QUERY = 'SELECT item_id FROM items WHERE item_name LIKE %s;'

    db = DB().connect()
    cur = db.cursor()
    try:
        cur.execute(QUERY, (name,))
        res = cur.fetchone()
    except sql_err.ProgrammingError as exc:
        raise ValueError(exc.msg)
    finally:
        cur.close()
        db.close()

    if res:
        return res[0]
    else:
        return


if __name__ == '__main__':
    print(get_item_by_name('Книга - Браконьер'))
    print(get_item_by_id(14972))
    # check_items()
