from commands import Command

from DB import autobuffer_list as buff

from config import creator_id

from utils import keyboards
from utils.buffs import APOSTOL_ITEM_ID, WARLOCK_ITEM_ID, PALADIN_ITEM_ID, CRUSADER_ITEM_ID, LIGHT_INC_ITEM_ID

from vk_bot.vk_bot import VkBot
from vk_api.bot_longpoll import VkBotEvent

# TODO: Add commands for paladin stuff by reply/for self


class ChangeBufferState(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('баффер', 'бафер', 'buffer'), access='creator')
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
        super().__init__(__class__.__name__, ('апо', 'apo'), access='guild')
        self.desc = 'Апостолы и их баффы. Только для членов гильдии'
        # self.set_active(False)
        return

    def run(self, bot: VkBot, event: VkBotEvent):
        from profile_api import get_voices

        apostols = buff.get_buffers_by_type(APOSTOL_ITEM_ID)

        if not apostols:
            bot.api.send_chat_msg(event.chat_id, "Мне жаль, но сейчас нет ни одного активного апостола")
            return

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


class Warlock(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('прокли', 'дебаф', 'дебафф', 'debuff', 'debuf'), access='guild')
        self.desc = 'Чернокнижники и их дебаффы. Только для членов гильдии'
        # self.set_active(False)
        return

    def run(self, bot: VkBot, event: VkBotEvent):

        warlocks = buff.get_buffers_by_type(WARLOCK_ITEM_ID)
        if not warlocks:
            bot.api.send_chat_msg(event.chat_id, "Мне жаль, но сейчас нет ни одного активного чернокнижника")
            return

        msg_id = event.message.conversation_message_id
        for buffer in warlocks:

            kbd = keyboards.warlock(buffer['id_vk'], msg_id, event.chat_id)
            bot.api.send_chat_msg(event.chat_id, f"[id{buffer['id_vk']}|Чернокнижник]", kbd=kbd)

        return


class PaladinStuff(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('травма', 'очистка', 'trauma', 'clear'), access='guild')
        self.desc = 'Паладины и производные классы и их заклинания. Только для членов гильдии'
        # self.set_active(False)
        return

    def run(self, bot: VkBot, event: VkBotEvent):

        paladins = buff.get_buffers_by_type(PALADIN_ITEM_ID)
        crusaders = buff.get_buffers_by_type(CRUSADER_ITEM_ID)
        light_incs = buff.get_buffers_by_type(LIGHT_INC_ITEM_ID)

        if not any([paladins, crusaders, light_incs]):
            bot.api.send_chat_msg(event.chat_id, "Мне жаль, но сейчас нет ни одного активного паладина")
            return

        msg_id = event.message.conversation_message_id

        if paladins:
            for buffer in paladins:
                kbd = keyboards.paladin(buffer['id_vk'], msg_id, event.chat_id)
                bot.api.send_chat_msg(event.chat_id, f"[id{buffer['id_vk']}|Паладин]", kbd=kbd)
        if crusaders:
            for buffer in crusaders:
                kbd = keyboards.crusader(buffer['id_vk'], msg_id, event.chat_id)
                bot.api.send_chat_msg(event.chat_id, f"[id{buffer['id_vk']}|Крестоносец]", kbd=kbd)
        if light_incs:
            for buffer in light_incs:
                kbd = keyboards.light_inc(buffer['id_vk'], msg_id, event.chat_id)
                bot.api.send_chat_msg(event.chat_id, f"[id{buffer['id_vk']}|Воплощение света]", kbd=kbd)
        return
