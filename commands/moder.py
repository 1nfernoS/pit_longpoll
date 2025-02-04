from commands import Command

from ORM import Session, UserInfo, Role, Logs

from dictionaries.emoji import gold
from dictionaries.roles import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from vk_api.bot_longpoll import VkBotEvent
    from vk_bot.vk_bot import VkBot


def toggle_role(id_from: int, id_to: int, role_id: int, toggle_role_id: int) -> str:
    s = Session()
    user_from: UserInfo = s.query(UserInfo).filter(UserInfo.user_id == id_from).first()

    if not user_from.user_role.role_can_change_role:
        return "Нет прав менять роль"

    user_to: UserInfo = s.query(UserInfo).filter(UserInfo.user_id == id_to).first()

    if not user_to:
        return f"О id{user_to.user_id} нет записей, пусть покажет профиль хотя бы раз!"

    if user_from.role_id > user_to.role_id:
        return "Вы не можете менять роль старшего по статусу"

    user_to.role_id = toggle_role_id \
        if user_to.role_id == role_id else role_id

    role: Role = s.query(Role).filter(Role.role_id == user_to.role_id).first()
    msg = f"Теперь @id{user_to.user_id} имеет права {role.role_name}"

    s.add(user_to)
    s.commit()
    s.close()
    return msg


class Kick(Command):
    # TODO: resolve error with kick etc

    def __init__(self):
        super().__init__(__class__.__name__, ('kick', 'кик'))
        self.desc = 'Кикнуть из чата. Доступно только модераторам гильдии'
        self.require_kick = True
        # self.set_active(False)
        return

    def run(self, bot: "VkBot", event: "VkBotEvent"):
        s = Session()

        user: UserInfo = s.query(UserInfo).filter(UserInfo.user_id == event.message.from_id).first()

        if not user.user_role.role_can_kick:
            return

        if 'reply_message' not in event.message.keys():
            bot.api.send_chat_msg(event.chat_id, 'Некого кикать... (по реплаю)')
            return

        if event.message.reply_message['from_id'] == event.message.from_id:
            return

        Logs(event.message.from_id, __class__.__name__,
             event.message.text,
             event.message.reply_message['text'],
             event.message.reply_message['from_id']
             ).make_record()

        kicked_user: UserInfo = \
            s.query(UserInfo).filter(UserInfo.user_id == event.message.reply_message['from_id']).first()

        if kicked_user:
            kicked_user.role_id = blacklist
            s.add(kicked_user)
            s.commit()

        bot.api.kick(event.chat_id, event.message.reply_message['from_id'])
        s.close()
        return


class Pin(Command):

    def __init__(self):
        super().__init__(__class__.__name__, ('pin', 'пин', 'закреп'))
        self.desc = 'Закрепить сообщение. Доступно только модераторам гильдии'
        self.require_moderate = True
        self.set_active(False)
        return

    def run(self, bot: "VkBot", event: "VkBotEvent"):
        s = Session()

        user: UserInfo = s.query(UserInfo).filter(UserInfo.user_id == event.message.from_id).first()

        if not user.user_role.role_can_moderate:
            return

        if 'reply_message' in event.message.keys():
            bot.api.pin_msg(event.chat_id, event.message.reply_message['conversation_message_id'])
            Logs(event.message.from_id, __class__.__name__, event.message.text, event.message.reply_message['text']).make_record()
        else:
            bot.api.send_chat_msg(event.chat_id, 'Нет реплая для закрепа...')
        s.close()
        return


class Check(Command):

    def __init__(self):
        super().__init__(__class__.__name__, ('счет', 'check', 'чек'))
        self.desc = 'Изменить баланс по реплаю на число (или -число). Доступно казначею и лидерам гильдии'
        self.require_change_balance = True
        # self.set_active(False)
        return

    def run(self, bot: "VkBot", event: "VkBotEvent"):
        s = Session()

        user: UserInfo = s.query(UserInfo).filter(UserInfo.user_id == event.message.from_id).first()

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

        Logs(event.message.from_id, __class__.__name__,
             event.message.text,
             event.message.reply_message['text'],
             event.message.reply_message['from_id']
             ).make_record()

        changed_user: UserInfo = s.query(UserInfo).filter(
            UserInfo.user_id == event.message.reply_message['from_id']).first()

        if changed_user is None:
            bot.api.send_chat_msg(event.chat_id, "Я не могу изменять баланс тем, кого не знаю, "
                                                 "пусть покажет профиль хоть раз, чтобы убедится, что это согильдиец!")
            return

        changed_user.balance += money

        s.add(changed_user)
        s.commit()

        bot.api.send_chat_msg(event.chat_id, f"Готово, изменил баланс на {money}{gold}, "
                                             f"теперь на счету {changed_user.balance}{gold}")
        return


class ToggleLeader(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('лид', 'leader', 'lead', 'лидер'))
        self.desc = 'Назначить лидера. Только для создателя'
        self.require_utils = True
        # self.set_active(False)
        return

    def run(self, bot: "VkBot", event: "VkBotEvent"):
        s = Session()

        user: UserInfo = s.query(UserInfo).filter(UserInfo.user_id == event.message.from_id).first()

        if not user.user_role.role_can_utils:
            return

        if 'reply_message' in event.message.keys():

            Logs(event.message.from_id, __class__.__name__, None, None,
                 event.message.reply_message['from_id']).make_record()

            msg = toggle_role(
                user.user_id,
                event.message.reply_message['from_id'],
                Role.leader_role().role_id,
                Role.guild_role().role_id
            )

            bot.api.send_chat_msg(event.chat_id, msg)
        s.close()
        return


class ToggleCaptain(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('капитан', 'captain'))
        self.desc = 'Назначить капитана. Для лидеров'
        self.require_change_role = True
        # self.set_active(False)
        return

    def run(self, bot: "VkBot", event: "VkBotEvent"):
        s = Session()

        user: UserInfo = s.query(UserInfo).filter(UserInfo.user_id == event.message.from_id).first()

        if not user.user_role.role_can_change_role:
            return

        if 'reply_message' in event.message.keys():

            Logs(event.message.from_id, __class__.__name__, None, None,
                 event.message.reply_message['from_id']).make_record()

            msg = toggle_role(
                event.message.from_id,
                event.message.reply_message['from_id'],
                Role.captain_role().role_id,
                Role.guild_role().role_id
            )
            bot.api.send_chat_msg(event.chat_id, msg)
        s.close()
        return


class ToggleOfficer(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('офицер', 'officer'))
        self.desc = 'Назначить офицера. Для лидеров'
        self.require_change_role = True
        # self.set_active(False)
        return

    def run(self, bot: "VkBot", event: "VkBotEvent"):
        s = Session()

        user: UserInfo = s.query(UserInfo).filter(UserInfo.user_id == event.message.from_id).first()

        if not user.user_role.role_can_change_role:
            return

        if 'reply_message' in event.message.keys():

            Logs(event.message.from_id, __class__.__name__, None, None,
                 event.message.reply_message['from_id']).make_record()

            msg = toggle_role(
                event.message.from_id,
                event.message.reply_message['from_id'],
                Role.officer_role().role_id,
                Role.guild_role().role_id
            )
            bot.api.send_chat_msg(event.chat_id, msg)
        s.close()
        return


class ToggleGuildMember(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('соги', 'согильдиец', 'member'))
        self.desc = 'Назначить согильдийца. Для лидеров и офицеров'
        self.require_change_role = True
        # self.set_active(False)
        return

    def run(self, bot: "VkBot", event: "VkBotEvent"):
        s = Session()

        user: UserInfo = s.query(UserInfo).filter(UserInfo.user_id == event.message.from_id).first()

        if not user.user_role.role_can_change_role:
            return

        if 'reply_message' in event.message.keys():

            Logs(event.message.from_id, __class__.__name__, None, None,
                 event.message.reply_message['from_id']).make_record()

            msg = toggle_role(
                event.message.from_id,
                event.message.reply_message['from_id'],
                Role.guild_role().role_id,
                Role.other_role().role_id
            )
            bot.api.send_chat_msg(event.chat_id, msg)
        s.close()
        return


class ToggleNewbie(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('новичок', 'испытательный', 'newbie'))
        self.desc = 'Назначить роль новичка. Для лидеров и офицеров'
        self.require_change_role = True
        # self.set_active(False)
        return

    def run(self, bot: "VkBot", event: "VkBotEvent"):
        s = Session()

        user: UserInfo = s.query(UserInfo).filter(UserInfo.user_id == event.message.from_id).first()

        if not user.user_role.role_can_change_role:
            return

        if 'reply_message' in event.message.keys():

            Logs(event.message.from_id, __class__.__name__, None, None,
                 event.message.reply_message['from_id']).make_record()

            msg = toggle_role(
                event.message.from_id,
                event.message.reply_message['from_id'],
                Role.newbie_role().role_id,
                Role.other_role().role_id
            )
            bot.api.send_chat_msg(event.chat_id, msg)
        s.close()
        return


class ToggleGuest(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('guest', 'гость'))
        self.desc = 'Назначить гостя. Для лидеров и офицеров'
        self.require_change_role = True
        # self.set_active(False)
        return

    def run(self, bot: "VkBot", event: "VkBotEvent"):
        s = Session()

        user: UserInfo = s.query(UserInfo).filter(UserInfo.user_id == event.message.from_id).first()

        if not user.user_role.role_can_change_role:
            return

        if 'reply_message' in event.message.keys():

            Logs(event.message.from_id, __class__.__name__, None, None,
                 event.message.reply_message['from_id']).make_record()

            msg = toggle_role(
                event.message.from_id,
                event.message.reply_message['from_id'],
                Role.guest_role().role_id,
                Role.other_role().role_id
            )
            bot.api.send_chat_msg(event.chat_id, msg)
        s.close()
        return
