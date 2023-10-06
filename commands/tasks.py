from datetime import datetime, timedelta

from commands import Command

from ORM import session, UserInfo, Task, Logs

from tasks.exec_task import remind

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from vk_api.bot_longpoll import VkBotEvent
    from vk_bot.vk_bot import VkBot


class Remind(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('напомни', 'remind', 'пингани'))
        self.desc = 'Напомнить через час о чем-либо'
        self.require_basic = True
        # self.set_active(False)
        return

    def run(self, bot: "VkBot", event: "VkBotEvent"):
        s = session()
        user: UserInfo = s.query(UserInfo).filter(UserInfo.user_id == event.message.from_id).first()

        if not user.user_role.role_can_basic:
            return

        Logs(event.message.from_id, __class__.__name__,
             reason=remind.__name__ + ': ' + event.message.text).make_record()
        args = {
            'user_id': event.message.from_id,
            'text': ' '.join(event.message.text.split()[1:]),
            'msg_id': bot.api.get_conversation_msg(event.message.peer_id, event.message.conversation_message_id)['id']
        }
        Task(datetime.utcnow() + timedelta(hours=1+3), remind, args).add()

        bot.api.send_chat_msg(event.chat_id, 'Хорошо, напомню через часик')
        s.close()
        return

