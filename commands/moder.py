from commands import Command, DB, ORM

# from DB import users

from utils.emoji import gold

# import for typing hints
from vk_api.bot_longpoll import VkBotEvent
from vk_bot.vk_bot import VkBot


class Kick(Command):

    def __init__(self):
        super().__init__(__class__.__name__, ('kick', 'кик'))
        self.desc = 'Кикнуть из чата. Доступно только модераторам гильдии'
        self.require_kick = True
        # self.set_active(False)
        return

    def run(self, bot: VkBot, event: VkBotEvent):
        user: ORM.UserInfo = DB.query(ORM.UserInfo).filter(ORM.UserInfo.user_id == event.message.from_id).first()

        if not user.user_role.role_can_kick:
            return

        if 'reply_message' not in event.message.keys():
            bot.api.send_chat_msg(event.chat_id, 'Некого кикать... (по реплаю)')
            return

        if event.message.reply_message['from_id'] == event.message.from_id:
            return

        kicked_user: ORM.UserInfo = \
            DB.query(ORM.UserInfo).filter(ORM.UserInfo.user_id == event.message.reply_message['from_id']).first()
        # users.update_user(event.message.reply_message['from_id'], is_active=False)
        role_blacklist: ORM.Role = DB.query(ORM.Role).filter(ORM.Role.role_id == 9).first()

        kicked_user.role_id = role_blacklist.role_id
        DB.add(kicked_user)
        DB.commit()

        bot.api.kick(event.chat_id, kicked_user.user_id)

        return


class Pin(Command):

    def __init__(self):
        super().__init__(__class__.__name__, ('pin', 'пин', 'закреп'))
        self.desc = 'Закрепить сообщение. Доступно только модераторам гильдии'
        self.require_moderate = True
        self.set_active(False)
        return

    def run(self, bot: VkBot, event: VkBotEvent):
        user: ORM.UserInfo = DB.query(ORM.UserInfo).filter(ORM.UserInfo.user_id == event.message.from_id).first()

        if not user.user_role.role_can_moderate:
            return

        if 'reply_message' in event.message.keys():
            bot.api.pin_msg(event.chat_id, event.message.reply_message['conversation_message_id'])
        else:
            bot.api.send_chat_msg(event.chat_id, 'Нет реплая для закрепа...')
        return


class Check(Command):

    def __init__(self):
        super().__init__(__class__.__name__, ('счет', 'check', 'чек'))
        self.desc = 'Изменить баланс по реплаю на число (или -число). Доступно казначею и лидерам гильдии'
        self.require_change_balance = True
        # self.set_active(False)
        return

    def run(self, bot: VkBot, event: VkBotEvent):
        user: ORM.UserInfo = DB.query(ORM.UserInfo).filter(ORM.UserInfo.user_id == event.message.from_id).first()

        if not user.user_role.role_can_change_balance:
            return

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

        changed_user: ORM.UserInfo = DB.query(ORM.UserInfo).filter(ORM.UserInfo.user_id == event.message.reply_message['from_id']).first()

        if changed_user is None:
            bot.api.send_chat_msg(event.chat_id, "Я не могу изменять баланс тем, кого не знаю, "
                                                 "пусть покажет профиль хоть раз, чтобы убедится, что это согильдиец!")
            return

        changed_user.balance += money

        DB.add(changed_user)
        DB.commit()

        bot.api.send_chat_msg(event.chat_id, f"Готово, изменил баланс на {money}{gold}, "
                                             f"теперь счету {changed_user.balance}{gold}")
        return
