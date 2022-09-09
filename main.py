from config import group_data
from vk_bot.vk_bot import VkBot

from messages.messages import new_message
from messages.events import event_message


def make_log():
    import time

    msg = time.strftime('%d.%m.%y %H:%M')
    msg += r'''
    Что сделать и что уже сделано
    '''
    bot.api.pin_msg(1, msg)


if __name__ == '__main__':
    bot = VkBot('kitty_dev[Test_Subj#001]', group_data['group_token'], group_data['group_id'])
    bot.set_handler('MESSAGE_NEW', new_message)
    bot.set_handler('MESSAGE_EVENT', event_message)

    bot.start()
