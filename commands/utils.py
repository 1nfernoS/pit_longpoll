from commands import Command

from config import creator_id

# import for typing hints
from vk_api.bot_longpoll import VkBotEvent
from vk_bot.vk_bot import VkBot


class Ping(Command):

    desc = 'Проверка живой я или нет'

    def __init__(self):
        super().__init__(__class__.__name__, ('ping', 'пинг', 'тык'))
        # self.set_active(False)
        return

    def run(self, bot: VkBot, event: VkBotEvent):
        bot.api.send_chat_msg(event.chat_id, 'Я живой)')
        return


class Role(Command):

    desc = 'Узнать роль свою или по реплаю/форварду. Только для создателя'

    def __init__(self):
        super().__init__(__class__.__name__, ('роль', 'role'))
        self.set_active(False)
        return

    def run(self, bot: VkBot, event: VkBotEvent):
        if event.message.from_id == int(creator_id):
            if 'reply_message' in event.message.keys():
                bot.api.send_chat_msg(event.chat_id, 'Ты роли пропиши сначала... Зря # TODO чтоль прописывал?')
            else:
                bot.api.send_chat_msg(event.chat_id, 'Нет ролей не команды, ты знаешь правила')
        return


class Id(Command):

    desc = 'Узнать ид свой или по реплаю. Только для создателя'

    def __init__(self):
        super().__init__(__class__.__name__, ('ид', 'id'))
        # self.set_active(False)
        return

    def run(self, bot: VkBot, event: VkBotEvent):
        if event.message.from_id == int(creator_id):
            if 'reply_message' in event.message.keys():
                bot.api.send_chat_msg(event.chat_id, str(event.message.reply_message['from_id']))
                pass
            else:
                bot.api.send_chat_msg(event.chat_id, str(event.message.from_id))
        return

