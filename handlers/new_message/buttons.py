import json
from datetime import datetime, timedelta

from ORM import Session, Notes

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from vk_bot.vk_bot import VkBot
    from vk_api.bot_longpoll import VkBotEvent


def payloads(self: "VkBot", event: "VkBotEvent"):
    if 'restore' in event.message.payload:
        restore_announce(self, event)
        return
    return


def restore_announce(self: "VkBot", event: "VkBotEvent"):
    pl = json.loads(event.message.payload)

    s = Session()

    note: Notes = s.query(Notes).filter(Notes.note_id == pl['restore']).first()
    if not note:
        if event.from_chat:
            self.api.send_chat_msg(event.chat_id, "Нет такого объявления")
            return
        if event.from_user:
            self.api.send_user_msg(event.message.from_id, "Нет такого объявления")
            return

    note.is_active = True
    note.expires_in = datetime.utcnow() + timedelta(hours=168+3)
    s.add(note)
    s.commit()
    if event.from_chat:
        self.api.send_chat_msg(event.chat_id, "Восстановил объявление")
    if event.from_user:
        self.api.send_user_msg(event.message.from_id, "Восстановил объявление")

    s.close()
    return
