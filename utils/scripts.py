from typing import List

from config import GUILD_CHAT_ID, creator_id

from ORM import session, UserInfo, Item

from profile_api import get_name, price


def withdraw_bill(members: List[int]) -> None:
    DB = session()
    for user_id in members:
        if user_id < 0:
            continue
        user: UserInfo = DB.query(UserInfo).filter(UserInfo.user_id == user_id).first()
        if not user:
            continue

        if user.user_role.role_can_balance:
            if user.user_id == creator_id:
                continue
            user.balance -= user.user_stats.user_level*140

        DB.add(user)

    DB.commit()
    return


def get_chat_id(token: str):
    import vk_api
    from vk_api.longpoll import VkEventType, VkLongPoll, CHAT_START_ID
    vk = vk_api.VkApi(token=token, api_version='5.131')
    api = vk.get_api()
    dialoges = api.messages.getConversations()
    chats = [i for i in dialoges['items'] if i['conversation']['peer']['type'] == 'chat']
    for chat in chats:
        if chat['conversation']['chat_settings']['title'] == 'Чат Гильдии "Тёмная сторона"':
            return chat['conversation']['peer']['local_id']


def update_items(start_id: int, stop_id: int) -> None:
    with session() as db:
        item_list = {}
        for i in range(start_id, stop_id):
            n = get_name(i)
            if n == '':
                continue

            item_list[i] = {'name': n, 'sell': int(price(i) > 0)}

            search: Item = db.query(Item).filter(Item.item_id == int(i)).first()
            if search:
                search.item_name = item_list[i]['name']
                search.item_has_price = bool(item_list[i]['sell'])
            else:
                search = Item(int(i), item_list[i]['name'], bool(item_list[i]['sell']))
            db.add(search)
        db.commit()
    return
