from vk_bot.vk_bot import VkBot

from config import GUILD_CHAT_ID

import DB.users as users
import DB.user_data as user_data


def withdraw_bill(bot: VkBot) -> None:
    members = bot.api.get_members(GUILD_CHAT_ID)
    # print(members, end=', ')
    for user_id in members:
        print(user_id)
        if user_id < 0:
            continue
        data_user = user_data.get_user_data(user_id)
        if data_user:
            # print(data_user['level'])
            if data_user['level'] < 100:
                users.change_balance(user_id, -18000)
            else:
                users.change_balance(user_id, -36000)
    # bot.api.send_chat_msg(GUILD_CHAT_ID, 'С баланса списан месячный налог, проверить свой баланс можно командой баланс')
    print('Done')
    return


if __name__ == '__main__':
    import config
    config.load('prod')
    bot = VkBot(config.group_data['group_token'])
    # withdraw_bill(bot)
