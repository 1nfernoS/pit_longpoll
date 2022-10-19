import config
from vk_bot.vk_bot import VkBot

config.load('dev')
bot = VkBot(config.group_data['group_token'])


def make_log():
    import time

    msg = time.strftime('%d.%m.%y %H:%M')
    msg += r'''
    Что сделано и что сделать
    '''
    bot.api.pin_msg(1, msg)


if __name__ == '__main__':
    make_log()
    pass
