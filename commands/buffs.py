from commands import Command

from DB import autobuffer_list as buff

from config import creator_id

from utils import keyboards
from utils.buffs import APOSTOL_ITEM_ID

from vk_bot.vk_bot import VkBot
from vk_api.bot_longpoll import VkBotEvent



class ChangeBufferState(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('баффер', 'бафер', 'buffer'))
        self.desc = 'Вкл/Выкл баффера (Апо, Вопла и др). Только для создателя'
        # self.set_active(False)
        return

    def run(self, bot: VkBot, event: VkBotEvent):

        if event.message.from_id == int(creator_id):
            if 'reply_message' in event.message.keys():
                state = buff.get_buffer_by_id(event.message.reply_message['from_id'], is_active=False)['is_active']
                buff.update_buffers(event.message.reply_message['from_id'], is_active=not state)
                bot.api.send_chat_msg(event.chat_id, f"Баффер стал {not state} ")
        return


class Apostol(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('апо', 'apo'))
        self.desc = 'Апостолы и их бафы'
        # self.set_active(False)
        return

    def run(self, bot: VkBot, event: VkBotEvent):
        from profile_api import get_voices

        apostols = buff.get_buffers_by_type(APOSTOL_ITEM_ID)
        voices = {apo['id_vk']: get_voices(apo['profile_key'], apo['id_vk']) for apo in apostols}

        if not any(voices):
            bot.api.send_chat_msg(event.chat_id, "Мне жаль, но сейчас нет ни одного апостола с голосами")
            return

        msg_id = event.message.conversation_message_id
        for apo in apostols:
            if not voices[apo['id_vk']]:
                continue

            kbd = keyboards.apostol(apo['id_vk'], msg_id, event.chat_id, apo['race1'], apo['race2'])
            bot.api.send_chat_msg(event.chat_id, f"[id{apo['id_vk']}|Голос]: {voices[apo['id_vk']]}", kbd=kbd)

        return
