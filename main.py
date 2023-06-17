import config
from vk_bot.vk_bot import VkBot

from handlers.new_message import new_message
from handlers.events import event_message

from vk_api.bot_longpoll import VkBotEvent

bot = VkBot(config.group_token)


@bot.startup()
def before_start(b: VkBot, *args):
    # b.api.send_chat_msg(config.GUILD_CHAT_ID, 'Ну, я проснулся')
    # All stuff dor startup
    return


@bot.on_stop()
def before_stop(b: VkBot, *args):
    b.api.send_chat_msg(config.GUILD_CHAT_ID, 'Я спать, тыкайте [id158154503|его], если что')
    return


@bot.event_handler(event_type='MESSAGE_NEW')
def new_msg(b: bot, e: VkBotEvent):
    return new_message(b, e)


@bot.event_handler('MESSAGE_REPLY')
def dummy(b: bot, e: VkBotEvent):
    # empty def for avoid logs about no handler
    return


@bot.event_handler('MESSAGE_EDIT')
def dummy(b: bot, e: VkBotEvent):
    # empty def for avoid logs about no handler
    return


@bot.event_handler('MESSAGE_EVENT')
def event(b: bot, e: VkBotEvent):
    return event_message(b, e)


if __name__ == '__main__':
    bot.start()
    pass
