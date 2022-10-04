from config import group_data
from vk_bot.vk_bot import VkBot

from messages.messages import new_message
from messages.events import event_message


def startup():
    # All before start()
    # TODO: Check builds
    print(' .'*20)
    return


if __name__ == '__main__':
    bot = VkBot('kitty_prod[asstrickster_kitty]', group_data['group_token'], group_data['group_id'])
    bot.before_start = startup
    bot.set_handler('MESSAGE_NEW', new_message)
    bot.set_handler('MESSAGE_EVENT', event_message)

    bot.start()
