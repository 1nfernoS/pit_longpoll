from datetime import datetime, timedelta

from commands import Command

import dictionaries.emoji as e
from ORM import session, UserInfo, Task, Logs, Notes

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
            'msg_id': bot.api.get_conversation_msg(event.message.peer_id, event.message.conversation_message_id)['id'],
            'type': 'remind'
        }
        Task(datetime.utcnow() + timedelta(hours=1+3), remind, args).add()

        bot.api.send_chat_msg(event.chat_id, 'Хорошо, напомню через часик')
        s.close()
        return


class Announce(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('объява', 'объявы', 'объявление', 'announce'))
        self.desc = '"добавить текст" или "удалить число" или "список/мои". Управление объявлениями в гильдии'
        self.require_basic = True
        # self.set_active(False)
        return

    def run(self, bot: "VkBot", event: "VkBotEvent"):
        s = session()
        user: UserInfo = s.query(UserInfo).filter(UserInfo.user_id == event.message.from_id).first()

        if not user.user_role.role_can_basic:
            return

        adding = ('добавить', 'add')
        deletion = ('удалить', 'delete', 'remove')
        listing = ('мои', 'список', 'list')

        msg = event.message.text.split()
        if len(msg) < 3 and msg[1].lower() not in listing:
            bot.api.send_chat_msg(event.chat_id, "Не хватает аргументов")
            return

        if msg[1].lower() not in adding+deletion+listing:
            bot.api.send_chat_msg(event.chat_id, 'Я могу удалить и добавить объявление, проверь команду')
            return

        Logs(event.message.from_id, __class__.__name__, reason=event.message.text[:200]+'...').make_record()

        if msg[1].lower() in adding:
            note = ' '.join(msg[2:])
            if len(note) > 255:
                bot.api.send_chat_msg(event.chat_id,
                                      f"Максимум 255 символов в объявлении, у вас {len(note)} (эмодзи едят по 6-10 символов)")
                s.close()
                return
            Notes(event.message.from_id, note).create()
            bot.api.send_chat_msg(event.chat_id, "Добавил твое объявление в газету!")

        elif msg[1].lower() in deletion:
            try:
                note_id = int(msg[2])
            except ValueError:
                bot.api.send_chat_msg(event.chat_id, "Для удаления объявления ме нужен его номер")
                s.close()
                return
            note: Notes = s.query(Notes).filter(Notes.note_id == note_id).first()
            if not note:
                bot.api.send_chat_msg(event.chat_id, "Не могу найти объявление")
                s.close()
                return
            if note.note_author != event.message.from_id and not user.user_role.role_can_utils:
                bot.api.send_chat_msg(event.chat_id, "Это не твое объявление!")
                s.close()
                return

            note.is_active = False
            s.add(note)
            s.commit()
            bot.api.send_chat_msg(event.chat_id, "Объявление удалено!")
        elif msg[1].lower() in listing:
            notes: Notes = s.query(Notes).filter(Notes.note_author == user.user_id, Notes.is_active==True).all()
            if not notes:
                bot.api.send_chat_msg(event.chat_id, 'У вас сейчас нет объявлений!')
                s.close()
                return
            answer = f"Ваши объявления:"
            for note in notes:
                answer += f"\n{note.note_id} -{e.tab}{note.note_text} (до {note.expires_in})"
            bot.api.send_chat_msg(event.chat_id, answer)

        s.close()
        return
