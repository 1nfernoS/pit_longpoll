import config
from vk_bot.vk_bot import VkBot

from handlers.new_message import new_message
from handlers.events import event_message

from vk_api.bot_longpoll import VkBotEvent

config.load('prod')
bot = VkBot(config.group_data['group_token'])


# TODO:
#   - logging
#   - puzzle hints (reply  with answer)
#   - APO system
#   - logs for economics
#   - SIGTERM handler for shell
#   - rework profile price with usage of `has_price`

@bot.startup()
def before_start(b: VkBot):
    b.api.send_chat_msg(config.GUILD_CHAT_ID, 'Ну, я проснулся')
    # All stuff dor startup
    return


@bot.on_stop()
def before_stop(b: VkBot):
    b.api.send_chat_msg(config.GUILD_CHAT_ID, 'Я спать, тыкайте [id158154503|его], если что')
    return


@bot.event_handler(event_type='MESSAGE_NEW')
def new_msg(b: bot, e: VkBotEvent):
    return new_message(b, e)


@bot.event_handler('MESSAGE_EDIT')
def edit(b: bot, e: VkBotEvent):
    # empty def for avoid logs about no handler
    return


@bot.event_handler('MESSAGE_EVENT')
def event(b: bot, e: VkBotEvent):
    return event_message(b, e)


if __name__ == '__main__':
    bot.start()
