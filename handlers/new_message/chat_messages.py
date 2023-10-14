import commands

from .buttons import payloads

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from vk_bot.vk_bot import VkBot
    from vk_api.bot_longpoll import VkBotEvent


def chat_message(self: "VkBot", event: "VkBotEvent"):
    if 'payload' in event.message:
        payloads(self, event)
        return

    # Potential command parse
    txt = event.message.text.lower().split()
    if not txt[0][0].isalnum():
        txt[0] = txt[0][1:]

    for cmd in commands.command_list:
        if txt[0] in cmd:
            commands.command_list[cmd].run(self, event)

    return
