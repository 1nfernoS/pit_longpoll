from commands import Command

from DB import users

# import for typing hints
from vk_api.bot_longpoll import VkBotEvent
from vk_bot.vk_bot import VkBot


class Kick(Command):

    def __init__(self):
        super().__init__(__class__.__name__, ('kick', 'кик'), 'leader')
        self.set_access('leader')
        self.desc = 'Кикнуть из чата. Доступно только лидерам гильдии'
        # self.set_active(False)
        return

    def run(self, bot: VkBot, event: VkBotEvent):
        if event.message.from_id in users.get_leaders():
            if 'reply_message' in event.message.keys():
                if event.message.reply_message['from_id'] != event.message.from_id:
                    bot.api.kick(event.chat_id, event.message.reply_message['from_id'])
                    users.update_user(event.message.reply_message['from_id'], is_active=False)
                    pass
            else:
                bot.api.send_chat_msg(event.chat_id, 'Некого кикать... (по реплаю)')
        return
