from commands import Command

from config import creator_id

# import for typing hints
from vk_api.bot_longpoll import VkBotEvent
from vk_bot.vk_bot import VkBot

from DB import users


class Ping(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('ping', 'пинг', 'тык'))
        self.desc = 'Проверка живой я или нет'
        # self.set_active(False)
        return

    def run(self, bot: VkBot, event: VkBotEvent):
        bot.api.send_chat_msg(event.chat_id, 'Я живой)')
        return


class Role(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('роль', 'role'))
        self.set_access('creator')
        self.desc = 'Узнать роль свою или по реплаю/форварду. Только для создателя'
        self.set_active(False)
        return

    def run(self, bot: VkBot, event: VkBotEvent):
        if event.message.from_id == int(creator_id):
            if 'reply_message' in event.message.keys():
                bot.api.send_chat_msg(event.chat_id, 'Ты роли пропиши сначала... Зря # TODO что ли прописывал?')
            else:
                bot.api.send_chat_msg(event.chat_id, 'Нет ролей нет команды, ты знаешь правила')
        return


class Id(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('ид', 'id'))
        self.set_access('creator')
        self.desc = 'Узнать ид свой или по реплаю. Только для создателя'
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


class Emoji(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('emoji', 'эмодзи', 'смайл'))
        self.set_access('creator')
        self.desc = 'Код эмодзи. Только для создателя'
        # self.set_active(False)
        return

    def run(self, bot: VkBot, event: VkBotEvent):
        if event.message.from_id == int(creator_id):
            msg = event.message.text.encode('cp1251', 'xmlcharrefreplace').decode('cp1251')
            msg = msg.split(' ', 1)[1].replace('&#', '').replace(';', '')
            bot.api.send_chat_msg(event.chat_id, msg)
        return


class SetLeader(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('лид', 'leader', 'lead', 'лидер'))
        self.set_access('creator')
        self.desc = 'Изменить роль лидера. Только для создателю'
        # self.set_active(False)
        return

    def run(self, bot: VkBot, event: VkBotEvent):
        if event.message.from_id == int(creator_id):
            if 'reply_message' in event.message.keys():
                state = users.get_user(event.message.reply_message['from_id'])['is_leader']
                users.update_user(event.message.reply_message['from_id'], is_leader=not state)
                bot.api.send_chat_msg(event.chat_id, f"Установил статус лидера {not state}")
        return


class SetOfficer(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('офицер', 'officer'))
        self.set_access('creator')
        self.desc = 'Изменить роль лидера. Только для создателю'
        # self.set_active(False)
        return

    def run(self, bot: VkBot, event: VkBotEvent):
        if event.message.from_id == int(creator_id):
            if 'reply_message' in event.message.keys():
                state = users.get_user(event.message.reply_message['from_id'])['is_officer']
                users.update_user(event.message.reply_message['from_id'], is_officer=not state)
                bot.api.send_chat_msg(event.chat_id, f"Установил статус лидера {not state}")
        return
