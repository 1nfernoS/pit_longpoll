from vk_bot.vk_bot import VkBot

from config import GUILD_CHAT_ID

from ORM import session as DB
import ORM


def withdraw_bill(bot: VkBot) -> None:
    members = bot.api.get_members(GUILD_CHAT_ID)
    for user_id in members:
        if user_id < 0:
            continue
        user: ORM.UserInfo = DB.query(ORM.UserInfo).filter(ORM.UserInfo.user_id == user_id).first()
        if not user:
            continue
        user.balance -= 18000 if user.user_stats.user_level < 100 else 36000

        DB.add(user)

    DB.commit()
    return


if __name__ == '__main__':
    import config
    config.load('prod')
    bot = VkBot(config.group_data['group_token'])
    # withdraw_bill(bot)
