from commands import Command

from DB import users

from utils.emoji import gold_emoji

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
                    users.update_user(event.message.reply_message['from_id'], is_active=False)
                    bot.api.kick(event.chat_id, event.message.reply_message['from_id'])
                    pass
            else:
                bot.api.send_chat_msg(event.chat_id, 'Некого кикать... (по реплаю)')
        return


class Pin(Command):

    def __init__(self):
        super().__init__(__class__.__name__, ('pin', 'пин', 'закреп'), 'leader')
        self.desc = 'Закрепить сообщение. Доступно только лидерам гильдии'
        self.set_active(False)
        return

    def run(self, bot: VkBot, event: VkBotEvent):
        if event.message.from_id not in users.get_leaders():
            return

        if 'reply_message' in event.message.keys():
            bot.api.pin_msg(event.chat_id, event.message.reply_message['conversation_message_id'])
        else:
            bot.api.send_chat_msg(event.chat_id, 'Нет реплая для закрепа...')
        return


class Check(Command):

    def __init__(self):
        super().__init__(__class__.__name__, ('счет', 'check', 'чек'), 'leader')
        self.desc = 'Изменить баланс по реплаю на число (или -число). Доступно только лидерам гильдии'
        # self.set_active(False)
        return

    def run(self, bot: VkBot, event: VkBotEvent):
        if event.message.from_id in users.get_leaders():
            if 'reply_message' not in event.message.keys():
                bot.api.send_chat_msg(event.chat_id, 'Я не могу менять баланс никому...')
                return

            msg = event.message.text.split()
            if len(msg) != 2:
                bot.api.send_chat_msg(event.chat_id, 'Что-то не то, нужна лишь команда и число (можно со знаком)')
                return
            try:
                money = int(msg[1])
            except ValueError:
                bot.api.send_chat_msg(event.chat_id, 'Что-то не то, это не число')
                return
            cur_balance = users.change_balance(event.message.reply_message['from_id'], money)
            if cur_balance is None:
                answer = 'Я не могу изменять баланс тем, кого не знаю, пусть покажет профиль хоть раз, чтобы убедится, что это согильдиец!'
            else:
                answer = f'Готово, изменил баланс на {money}{gold_emoji}, теперь счету {cur_balance}{gold_emoji}'
            bot.api.send_chat_msg(event.chat_id, answer)
        return
