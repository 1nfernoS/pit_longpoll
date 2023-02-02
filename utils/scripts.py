from vk_bot.vk_bot import VkBot

from config import GUILD_CHAT_ID

import DB.users as users
import DB.user_data as user_data


def withdraw_bill(bot: VkBot) -> None:
    members = bot.api.get_members(GUILD_CHAT_ID)
    for user_id in members:
        print(user_id)
        if user_id < 0:
            continue
        data_user = user_data.get_user_data(user_id)
        if not data_user:
            continue
        users.change_balance(user_id,
                             -18000 if data_user['level'] < 100
                             else -36000)
    return


if __name__ == '__main__':
    import config
    config.load('prod')
    bot = VkBot(config.group_data['group_token'])
    # withdraw_bill(bot)
