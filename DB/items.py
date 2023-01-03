from DB import DB


def check_items():
    import os
    import json

    query = 'INSERT INTO `items` VALUES (%s, %s, %s);'
    items = json.loads(open(os.environ.get('ITEM_FILE'), 'r').read())

    for i in items:
        data = (i, *list(items[i].values()))
        DB().query(query, data)
    return


def get_item_by_id(item_id: int):
    query = 'SELECT item_name FROM items WHERE item_id = %s;'

    try:
        item_id = int(item_id)
    except ValueError:
        raise TypeError(f"`item_id` must be int, got {item_id} instead")

    res = DB().query(query, (item_id,))
    if res:
        res = res[0]
        return res[0]
    else:
        return


def get_item_by_name(name: str, has_price: bool = True):
    query = "SELECT item_id FROM items WHERE item_name LIKE CONCAT(%s, '%')"

    if has_price:
        query += " AND has_price = 1"

    res = DB().query(query, (name,))

    if res:
        res = res[0]
        return res[0]
    else:
        return


def search_item(name: str, has_price: bool = True):
    # query = "SELECT COUNT(*) FROM items WHERE item_name LIKE CONCAT('Книга - ', %s, '%')"
    query = "SELECT * FROM items WHERE item_name REGEXP CONCAT('(Книга - |Книга - [[:alnum:]]+ |^[[:alnum:]]+ |^)', %s, '.*$')"

    if has_price:
        query += " AND has_price = 1"
    '''
    cnt = DB().query(query, (name,))[0][0]
    if cnt > 0:
        query = "SELECT * FROM items WHERE item_name LIKE CONCAT('Книга - ', %s, '%');"
    else:
        query = "SELECT * FROM items WHERE item_name LIKE CONCAT(%s, '%');"
    
    if has_price:
        query += " AND has_price = 1"
    '''

    # query = "SELECT * FROM items WHERE item_name LIKE CONCAT('%', %s, '%');"

    res = DB().query(query, (name, ))
    if res:
        data = {'count': 0, 'result': []}
        for row in res:
            data['result'].append({'item_id': row[0], 'item_name': row[1]})
        data['count'] = len(data['result'])
        return data
    else:
        return


def search_regexp(item_name: str, has_price: bool = True) -> (dict, None):
    query = "SELECT * FROM items WHERE item_name REGEXP CONCAT('(Книга - |^)', %s, '$')"

    if has_price:
        query += " AND has_price = 1"

    data = DB().query(query, (item_name,))
    if data:
        res = {}
        for row in data:
            res[row[0]] = row[1]
        return res
    return


if __name__ == '__main__':
    # print(get_item_by_name('Браконьер'))
    # print(get_item_by_id(14972))
    print(search_item('про'))
    # check_items()
