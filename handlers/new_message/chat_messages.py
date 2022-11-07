# builtins
import logging
import time

# requirement's import
from vk_api.bot_longpoll import VkBotEvent

import commands

# import for typing hints
from vk_bot.vk_bot import VkBot


def chat_message(self: VkBot, event: VkBotEvent):
    # Potential command parse
    txt = event.message.text.lower().split()
    if not txt[0][0].isalnum():
        txt[0] = txt[0][1:]

    for cmd in commands.command_list:
        if txt[0] in cmd:
            logging.info(f"{time.strftime('%d %m %Y %H:%M:%S')}\t[{event.chat_id}]({event.message.from_id}): {txt[0]}")

            commands.command_list[cmd].run(self, event)
            msg_id = self.api.get_conversation_msg(event.message.peer_id, event.message.conversation_message_id)['id']
            self.api.del_msg(event.message.peer_id, msg_id)

    return
