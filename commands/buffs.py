from typing import List, TYPE_CHECKING

from ORM import Session, UserInfo, BuffUser, Logs
from commands import Command
from config import creator_id

from utils import keyboards
from dictionaries.buffs import APOSTOL_ITEM_ID, WARLOCK_ITEM_ID, PALADIN_ITEM_ID, CRUSADER_ITEM_ID, LIGHT_INC_ITEM_ID

from profile_api import get_voices

if TYPE_CHECKING:
    from vk_bot.vk_bot import VkBot
    from vk_api.bot_longpoll import VkBotEvent


class ToggleBuffer(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('баффер', 'бафер', 'buffer'))
        self.desc = 'Вкл/Выкл баффера (Апо, Вопла и др). Только для создателя'
        self.require_utils = True
        # self.set_active(False)
        return

    def run(self, bot: "VkBot", event: "VkBotEvent"):
        if event.message.from_id != creator_id:
            return

        if 'reply_message' not in event.message.keys():
            return

        user_id = event.message.reply_message['from_id']

        Logs(event.message.from_id, __class__.__name__, on_user_id=user_id).make_record()

        with Session() as s:
            buffer: BuffUser = s.query(BuffUser).filter(BuffUser.buff_user_id == user_id).first()
            buffer.buff_user_is_active = int(not bool(buffer.buff_user_is_active))
            s.add(buffer)
            s.commit()
            bot.api.send_chat_msg(event.chat_id, f"Баффер стал {bool(buffer.buff_user_is_active)} ")

        return


class Apostol(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('апо', 'apo'))
        self.desc = 'Апостолы и их баффы. Только для членов гильдии'
        self.require_get_buff = True
        # self.set_active(False)
        return

    def run(self, bot: "VkBot", event: "VkBotEvent"):

        s = Session()
        user: UserInfo = s.query(UserInfo).filter(UserInfo.user_id == event.message.from_id).first()
        if not user.user_role.role_can_get_buff:
            return

        Logs(event.message.from_id, __class__.__name__).make_record()


        apostols: List[BuffUser] = s.query(BuffUser).filter(BuffUser.buff_type_id == APOSTOL_ITEM_ID,
                                                            BuffUser.buff_user_is_active == 1).all()

        if not apostols:
            bot.api.send_chat_msg(event.chat_id, "Мне жаль, но сейчас нет ни одного активного апостола")
            return

        voices = {apo.buff_user_id: get_voices(apo.buff_user_profile_key, apo.buff_user_id) for apo in apostols}

        if not any(voices.values()):
            bot.api.send_chat_msg(event.chat_id, "Мне жаль, но сейчас нет ни одного апостола с голосами")
            return

        msg_id = event.message.conversation_message_id
        for apo in apostols:
            if not voices[apo.buff_user_id]:
                continue

            kbd = keyboards.apostol(apo.buff_user_id, msg_id, event.chat_id, apo.buff_user_race1, apo.buff_user_race2)
            bot.api.send_chat_msg(event.chat_id, f"[id{apo.buff_user_id}|Голос]: {voices[apo.buff_user_id]}", kbd=kbd)
        s.close()
        return


class Warlock(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('прокли', 'дебаф', 'дебафф', 'debuff', 'debuf'))
        self.desc = 'Чернокнижники и их дебаффы. Только для членов гильдии'
        # self.set_active(False)
        return

    def run(self, bot: "VkBot", event: "VkBotEvent"):
        s = Session()
        user: UserInfo = s.query(UserInfo).filter(UserInfo.user_id == event.message.from_id).first()
        if not user.user_role.role_can_get_buff:
            return

        Logs(event.message.from_id, __class__.__name__).make_record()

        warlocks: List[BuffUser] = s.query(BuffUser).filter(BuffUser.buff_type_id == WARLOCK_ITEM_ID,
                                                            BuffUser.buff_user_is_active == 1).all()

        if not warlocks:
            bot.api.send_chat_msg(event.chat_id, "Мне жаль, но сейчас нет ни одного активного чернокнижника")
            return
        
        voices = {buffer.buff_user_id: get_voices(buffer.buff_user_profile_key, buffer.buff_user_id)
                  for buffer in warlocks}
        
        if not any(voices.values()):
            bot.api.send_chat_msg(event.chat_id, "Мне жаль, но сейчас нет ни одного чернокнижника с голосами")
            return
        
        msg_id = event.message.conversation_message_id
        for buffer in warlocks:

            kbd = keyboards.warlock(buffer.buff_user_id, msg_id, event.chat_id)
            bot.api.send_chat_msg(event.chat_id,
                                  f"[id{buffer.buff_user_id}|Чернокнижник]: {voices[buffer.buff_user_id]}", kbd=kbd)
        s.close()
        return


class PaladinStuff(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('травма', 'травмы', 'очистка', 'trauma'))
        self.desc = 'Паладины и производные классы и их заклинания. Только для членов гильдии'
        # self.set_active(False)
        return

    def run(self, bot: "VkBot", event: "VkBotEvent"):

        s = Session()
        user: UserInfo = s.query(UserInfo).filter(UserInfo.user_id == event.message.from_id).first()
        if not user.user_role.role_can_get_buff:
            return

        Logs(event.message.from_id, __class__.__name__).make_record()

        paladins: List[BuffUser] = s.query(BuffUser).filter(BuffUser.buff_type_id == PALADIN_ITEM_ID,
                                                            BuffUser.buff_user_is_active == 1).all()
        crusaders: List[BuffUser] = s.query(BuffUser).filter(BuffUser.buff_type_id == CRUSADER_ITEM_ID,
                                                            BuffUser.buff_user_is_active == 1).all()
        light_incs: List[BuffUser] = s.query(BuffUser).filter(BuffUser.buff_type_id == LIGHT_INC_ITEM_ID,
                                                            BuffUser.buff_user_is_active == 1).all()

        if not any([paladins, crusaders, light_incs]):
            bot.api.send_chat_msg(event.chat_id, "Мне жаль, но сейчас нет ни одного активного паладина")
            return
        

        voices = {buffer.buff_user_id: get_voices(buffer.buff_user_profile_key, buffer.buff_user_id)
                  for buffer in paladins+crusaders+light_incs}

        if not any(voices.values()):
            bot.api.send_chat_msg(event.chat_id, "Мне жаль, но сейчас нет ни одного чернокнижника с голосами")
            return

        msg_id = event.message.conversation_message_id

        if paladins:
            for buffer in paladins:
                kbd = keyboards.paladin(buffer.buff_user_id, msg_id, event.chat_id)
                bot.api.send_chat_msg(event.chat_id,
                                      f"[id{buffer.buff_user_id}|Паладин]: {voices[buffer.buff_user_id]}", kbd=kbd)
        if crusaders:
            for buffer in crusaders:
                kbd = keyboards.crusader(buffer.buff_user_id, msg_id, event.chat_id)
                bot.api.send_chat_msg(event.chat_id,
                                      f"[id{buffer.buff_user_id}|Крестоносец]: {voices[buffer.buff_user_id]}", kbd=kbd)
        if light_incs:
            for buffer in light_incs:
                kbd = keyboards.light_inc(buffer.buff_user_id, msg_id, event.chat_id)
                bot.api.send_chat_msg(event.chat_id,
                                      f"[id{buffer.buff_user_id}|Воплощение света]: {voices[buffer.buff_user_id]}", kbd=kbd)
        s.close()
        return
