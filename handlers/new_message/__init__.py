from config import OVERSEER_BOT, PIT_BOT, ALLOWED_CHATS, LOGS_CHAT_ID

from .chat_messages import chat_message
from .direct_messages import user_message
from .group_messages import bot_message
from .forwards import forward_parse

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from vk_bot.vk_bot import VkBot
    from vk_api.bot_longpoll import VkBotEvent


def new_message(self: "VkBot", event: "VkBotEvent"):
    if event.from_user:
        user_message(self, event)
    if event.from_chat:
        if event.chat_id == LOGS_CHAT_ID:
            msg_del = self.api.get_conversation_msg(event.message.peer_id, event.message.conversation_message_id)['id']
            self.api.del_msg(event.message.peer_id, msg_del)
            return
        if event.chat_id not in ALLOWED_CHATS:
            return
        if event.message.from_id == OVERSEER_BOT:
            bot_message(self, event)
        elif event.message.text:
            chat_message(self, event)

    if len(event.message.fwd_messages) > 0:
        if int(event.message.fwd_messages[0]['from_id']) == PIT_BOT:
            forward_parse(self, event)
            pass
        return

    return
