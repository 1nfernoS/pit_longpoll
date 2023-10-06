from commands import Command

from ORM import session, UserInfo, Task, Logs

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from vk_api.bot_longpoll import VkBotEvent
    from vk_bot.vk_bot import VkBot


class Grib(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('гриб', 'grib'))
        self.desc = 'Проверка живой я или нет'
        self.require_basic = True
        # self.set_active(False)
        return

    def run(self, bot: "VkBot", event: "VkBotEvent"):
        s = session()
        user: UserInfo = s.query(UserInfo).filter(UserInfo.user_id == event.message.from_id).first()

        if not user.user_role.role_can_basic:
            return

        Logs(event.message.from_id, __class__.__name__).make_record()

        bot.api.send_chat_msg(event.chat_id, '&#127812;')
        s.close()
        return


class Pinok(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('пнуть',))
        self.desc = 'Пасхалка для Алексея Вьюгова'
        self.require_basic = True
        # self.set_active(False)
        return

    def run(self, bot: "VkBot", event: "VkBotEvent"):
        s = session()
        user: UserInfo = s.query(UserInfo).filter(UserInfo.user_id == event.message.from_id).first()

        if not user.user_role.role_can_basic:
            return

        if 'reply_message' not in event.message.keys():
            return

        if event.message.reply_message['from_id'] != -bot._group_id:
            return

        Logs(event.message.from_id, __class__.__name__,
             event.message.text,
             event.message.reply_message['text'],
             event.message.reply_message['from_id']
             ).make_record()
        msg_id = bot.api.get_conversation_msg(event.message.peer_id, event.message.conversation_message_id)['id']
        bot.api.send_chat_msg(event.chat_id, "",
                              reply_to=msg_id,
                              attachment='photo158154503_457293062_bd298a930a635413d9')
        s.close()
        return
