"""
Table autobuffer rely on tables
    buffer_type (which in fact item_id)
    and joined tables buff_list (all available buffs) with buffer_buff (which type can use which buff)
None of these tables require any frequent changes, so there is no DML code in module nor other modules
All tables and Pre-defined data are described in scripts/

(c) 1nfernoS
"""

from DB import DB


def load_buffer_buff():
    query = 'SELECT bb.buffer_id, bb.buff_id FROM buffer_buff bb ' \
            'JOIN buffer_type t ON bb.buffer_id=t.buffer_type_id JOIN buff_list l ON bb.buff_id=l.buff_list_id;'

    res = DB().query(query)

    data = {}
    for row in res:
        data[row[0]] = data.get(row[0], []) + [row[1]]

    return data


def get_buff_command(id_buff: int) -> str:
    query = 'SELECT buff_command FROM buff_list WHERE buff_list_id=%s;'

    try:
        id_buff = int(id_buff)
    except ValueError:
        raise TypeError(f"`id_buff` must be int, got {id_buff} instead")

    res = DB().query(query, (id_buff,))

    if res:
        return res[0][0]
    else:
        return


def add_autobuffer(id_vk: int, profile_key: str, is_active: bool, class_id: int):
    query = 'INSERT INTO `autobuffer_list` (id_vk, profile_key, is_active, buffer_type) VALUE ( %s, %s, %s, %s );'

    try:
        id_vk = int(id_vk)
    except ValueError:
        raise TypeError(f"`id_vk` must be int, got {id_vk} instead")

    try:
        class_id = int(class_id)
    except ValueError:
        raise TypeError(f"`class_id` must be int, got {class_id} instead")

    data = (id_vk, profile_key, is_active, class_id)

    DB().query(query, data)
    return


def get_buffer_by_id(id_vk: int, is_active: bool = True):
    query = 'SELECT id_vk, profile_key, token_key, buffer_type, race1, race2 FROM `autobuffer_list` WHERE id_vk = %s'

    if is_active:
        query += ' and is_active = 1;'

    try:
        id_vk = int(id_vk)
    except ValueError:
        raise TypeError(f"`id_vk` must be int, got {id_vk} instead")

    res = DB().query(query, (id_vk,))

    if res:
        res = res[0]
        return {'id_vk': res[0], 'profile_key': res[1], 'token_key': res[2], 'buffer_type': res[3],
                'race1': res[4], 'race2': res[5]}
    else:
        return


def get_peer_by_buffer_id(id_vk: int, bot_chat_id: int):
    query = 'SELECT peer_id FROM `autobuffer_chat` WHERE buffer_id = %s AND bot_chat_id = %s;'

    try:
        id_vk = int(id_vk)
    except ValueError:
        raise TypeError(f"`id_vk` must be int, got {id_vk} instead")

    try:
        bot_chat_id = int(bot_chat_id)
    except ValueError:
        raise TypeError(f"`bot_chat_id` must be int, got {bot_chat_id} instead")

    res = DB().query(query, (id_vk, bot_chat_id))

    if res:
        return res[0][0]
    else:
        return


def get_buffers_by_type(class_id: int, is_active: bool = True):

    query = 'SELECT id_vk, profile_key, token_key, buffer_type, race1, race2 ' \
            'FROM `autobuffer_list` WHERE buffer_type = %s'

    if is_active:
        query += ' and is_active = 1;'

    try:
        class_id = int(class_id)
    except ValueError:
        raise TypeError(f"`class_id` must be int, got {class_id} instead")

    res = DB().query(query, (class_id,))

    if res:
        result = []
        for row in res:
            result.append({'id_vk': row[0], 'profile_key': row[1], 'token_key': row[2], 'buffer_type': row[3],
                                   'race1': row[4], 'race2': row[5]})
        return result

    return


def update_buffers(id_vk: int, **kwargs):
    query = 'UPDATE `autobuffer_list` SET ' + ', '.join([k + ' = %s' for k in kwargs.keys()]) + ' WHERE id_vk = %s;'

    try:
        id_vk = int(id_vk)
    except ValueError:
        raise TypeError(f"`id_vk` must be int, got {id_vk} instead")

    data = tuple(kwargs.values())

    DB().query(query, (*data, id_vk))
    return
