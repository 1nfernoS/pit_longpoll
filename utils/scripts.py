from vk_bot.vk_bot import VkBot

from config import GUILD_CHAT_ID

from ORM import session, UserInfo


def withdraw_bill(bot: VkBot) -> None:
    members = bot.api.get_members(GUILD_CHAT_ID)
    DB = session()
    for user_id in members:
        if user_id < 0:
            continue
        user: UserInfo = DB.query(UserInfo).filter(UserInfo.user_id == user_id).first()
        if not user:
            continue

        if user.user_role.role_can_balance:
            user.balance -= 18000 if user.user_stats.user_level < 100 else 36000

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


if __name__ == '__main__':
    import config
    config.load('prod')
    bot = VkBot(config.group_data['group_token'])
    # withdraw_bill(bot)
