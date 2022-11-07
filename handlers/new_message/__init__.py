# builtins
import logging
import time

# requirement's import
from vk_api.bot_longpoll import VkBotEvent

# config and packages
from config import OVERSEER_BOT, PIT_BOT, ALLOWED_CHATS

from .chat_messages import chat_message
from .direct_messages import user_message
from .group_messages import bot_message
from .forwards import forward_parse

# import for typing hints
from vk_bot.vk_bot import VkBot


def new_message(self: VkBot, event: VkBotEvent):
    if event.from_user:
        user_message(self, event)
    if event.from_chat:
        if event.chat_id not in ALLOWED_CHATS:
            return
        if event.message.from_id == OVERSEER_BOT:
            bot_message(self, event)
        elif event.message.text:
            chat_message(self, event)

    if len(event.message.fwd_messages) == 1:
        if int(event.message.fwd_messages[0]['from_id']) == int(PIT_BOT):
            txt = event.message.fwd_messages[0]['text'].encode('cp1251', 'xmlcharrefreplace').decode('cp1251').replace('\n', ' | ')
            logging.info(f"{time.strftime('%d %m %Y %H:%M:%S')}\t[{event.chat_id}]({event.message.from_id}): {txt}")
            del txt

            forward_parse(self, event)
            pass
        return

    return
