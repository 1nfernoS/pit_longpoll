from config import group_data
from vk_bot.vk_bot import VkBot

from messages.messages import new_message
from messages.events import event_message

from vk_api.bot_longpoll import VkBotEvent

bot = VkBot('kitty_prod[asstrickster_kitty]', group_data['group_token'], group_data['group_id'])


@bot.startup()
def before_start(b: VkBot):
    # All stuff dor startup
    return


# TODO: make decorator work,
#  rework profile price with usage of `has_price`

@bot.on_stop()
def before_stop(b: VkBot):
    # All before exiting
    return


@bot.event_handler(event_type='MESSAGE_NEW')
def new_msg(b: bot, e: VkBotEvent):
    return new_message(b, e)


@bot.event_handler('MESSAGE_EVENT')
def event(b: bot, e: VkBotEvent):
    return event_message(b, e)


if __name__ == '__main__':
    bot.start()
