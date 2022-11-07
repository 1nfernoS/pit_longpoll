from commands import Command

from config import creator_id, GUILD_CHAT_ID, GUILD_NAME

# import for typing hints
from vk_api.bot_longpoll import VkBotEvent
from vk_bot.vk_bot import VkBot

from DB import users


class Ping(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('ping', 'пинг', 'тык'))
        self.desc = 'Проверка живой я или нет'
        # self.set_active(False)
        return

    def run(self, bot: VkBot, event: VkBotEvent):
        bot.api.send_chat_msg(event.chat_id, 'Я живой)')
        return


class War(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('war', 'война'), 'guild')
        self.desc = 'Список игроков, с которой идет война. Только для членов гильдии'
        # self.set_active(False)
        return

    def run(self, bot: VkBot, event: VkBotEvent):
        if event.message.from_id not in bot.api.get_members(GUILD_CHAT_ID):
            war_list = f'Нет, это только для членов гильдии {GUILD_NAME}!'
        else:
            # f"1. Имя Фамилия (расы - класс): &#128481;{attack} &#128737;{defence} &#128074;{strength} &#128400;{agility} &#10084;{endurance} &#127808;{luck}" \
            war_list = "Война с Кейнхерст:" \
                       r"""
                                  
Вадим Москвитес (эльф-гном - крестоносец): 
&#128481;:781 &#128737;:396 &#127808;:54
&#128074;:594 &#128400;:675 &#10084;:1072

Стас Ключников (человек-эльф - апостол): 
&#128481;:116 &#128737;:99 &#127808;:16
&#128074;:267 &#128400;:287 &#10084;:268

Святослав Карпов (человек - воплощение света): 
&#128481;:93 &#128737;:88 &#127808;:16
&#128074;:241 &#128400;:215 &#10084;:243

Мария Масюкова (гном-эльф - воплощение луны): 
&#128481;:261 &#128737;:177 &#127808;:41
&#128074;:502 &#128400;:507 &#10084;:516

Алексей Задатков (эльф-человек - апостол): 
&#128481;:210 &#128737;:44 &#127808;:27
&#128074;:320 &#128400;:349 &#10084;:323

Вадим Аксаков (человек-эльф - апостол): 
&#128481;:307 &#128737;:200 &#127808;:39
&#128074;:584 &#128400;:745 &#10084;:697

Саша Якубенко (человек-гном - апостол): 
&#128481;:545 &#128737;:332 &#127808;:55
&#128074;:715 &#128400;:717 &#10084;:709

Игорь Руснак (демон-нежить - апостол): 
&#128481;:351 &#128737;:229 &#127808;:43
&#128074;:539 &#128400;:673 &#10084;:668

Mr Pudge (орк-гном - дело в шляпе): 
&#128481;:437 &#128737;:282 &#127808;:50
&#128074;:625 &#128400;:648 &#10084;:646

Дима Димочка (гоблин - повелитель мрака): 
&#128481;:132 &#128737;:110 &#127808;:24
&#128074;:191 &#128400;:330 &#10084;:312

&#19973;&#21475; &#23665;&#21314; (эльф - прокаженный): 
&#128481;:104 &#128737;:79 &#127808;:17
&#128074;:153 &#128400;:208 &#10084;:235

Кирилл Краевский (эльф-гном - повелитель мрака): 
&#128481;:402 &#128737;:247 &#127808;:41
&#128074;:605 &#128400;:689 &#10084;:634

Павел Смирнов (гоблин-гном - злойглаз добраядуша): 
&#128481;:712 &#128737;:247 &#127808;:67
&#128074;:966 &#128400;:1036 &#10084;:882

Максим Блащенко (демон-эльф - повелитель мрака): 
&#128481;:199 &#128737;:165 &#127808;:26
&#128074;:280 &#128400;:279 &#10084;:299

Владислав Жиленко (гном-гоблин - валет плетей): 
&#128481;:645 &#128737;:235 &#127808;:40
&#128074;:406 &#128400;:874 &#10084;:622

Антон Александрович (демон-орк - королевский убийца): 
&#128481;:309 &#128737;:38 &#127808;:15
&#128074;:203 &#128400;:273 &#10084;:224

Анна Соколова (нежить-человек - клинок тьмы): 
&#128481;:284 &#128737;:188 &#127808;:27
&#128074;:393 &#128400;:395 &#10084;:419

Катя Михалева (гном - повелитель мрака): 
&#128481;:134 &#128737;:102 &#127808;:15
&#128074;:165 &#128400;:173 &#10084;:238

Сергей Ермаков (гоблин-гном - прокаженный): 
&#128481;:424 &#128737;:192 &#127808;:40
&#128074;:532 &#128400;:571 &#10084;:569

Ян Ставничук (гоблин-гном - берсеркер): 
&#128481;:748 &#128737;:276 &#127808;:63
&#128074;:602 &#128400;:970 &#10084;:988

Андрей Рахуба (гном-гоблин - повелитель мрака): 
&#128481;:393 &#128737;:344 &#127808;:39
&#128074;:103 &#128400;:653 &#10084;:367

Илья Кожихов (человек - королевский убийца): 
&#128481;:425 &#128737;:30 &#127808;:21
&#128074;:308 &#128400;:435 &#10084;:354
"""
        bot.api.send_chat_msg(event.chat_id, war_list)
        return

    def __template(self, bot: VkBot, event: VkBotEvent) -> str:
        """
        template generator for run
        :return:
        """
        msg = bot.api.messages.getByConversationMessageId(peer_id=2000000000 + GUILD_CHAT_ID,
                                                          conversation_message_ids=254530)['items'][0]
        res_text = [i['text'] for i in msg['fwd_messages']]
        res_str = ''
        for record in res_text:
            data = record.split('\n')
            name = data[0][24:-2]
            race = data[1][15:]
            class_ = data[2][16:]
            luck = data[5][16:]
            strength = data[6][15:]
            agility = data[7][19:]
            endurance = data[8][22:]
            attack = data[9][14:]
            defence = data[10][16:]
            res_str += f"\n{name} ({race} - {class_}): \n" \
                       f"&#128481;:{attack} &#128737;:{defence} &#127808;:{luck}\n" \
                       f"&#128074;:{strength} &#128400;:{agility} &#10084;:{endurance}\n"
        return res_str


class Role(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('роль', 'role'))
        self.set_access('creator')
        self.desc = 'Узнать роль свою или по реплаю/форварду. Только для создателя'
        self.set_active(False)
        return

    def run(self, bot: VkBot, event: VkBotEvent):
        if event.message.from_id == int(creator_id):
            if 'reply_message' in event.message.keys():
                bot.api.send_chat_msg(event.chat_id, 'Ты роли пропиши сначала... Зря # TODO что ли прописывал?')
            else:
                bot.api.send_chat_msg(event.chat_id, 'Нет ролей нет команды, ты знаешь правила')
        return


class Id(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('ид', 'id'))
        self.set_access('creator')
        self.desc = 'Узнать ид свой или по реплаю. Только для создателя'
        # self.set_active(False)
        return

    def run(self, bot: VkBot, event: VkBotEvent):
        if event.message.from_id == int(creator_id):
            if 'reply_message' in event.message.keys():
                bot.api.send_chat_msg(event.chat_id, str(event.message.reply_message['from_id']))
                pass
            else:
                bot.api.send_chat_msg(event.chat_id, str(event.message.from_id))
        return


class Emoji(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('emoji', 'эмодзи', 'смайл'))
        self.set_access('creator')
        self.desc = 'Код эмодзи. Только для создателя'
        # self.set_active(False)
        return

    def run(self, bot: VkBot, event: VkBotEvent):
        if event.message.from_id == int(creator_id):
            msg = event.message.text.encode('cp1251', 'xmlcharrefreplace').decode('cp1251')
            msg = msg.split(' ', 1)[1].replace('&#', '').replace(';', '')
            bot.api.send_chat_msg(event.chat_id, msg)
        return


class SetLeader(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('лид', 'leader', 'lead', 'лидер'))
        self.set_access('creator')
        self.desc = 'Изменить роль лидера. Только для создателю'
        # self.set_active(False)
        return

    def run(self, bot: VkBot, event: VkBotEvent):
        if event.message.from_id == int(creator_id):
            if 'reply_message' in event.message.keys():
                state = users.get_user(event.message.reply_message['from_id'])['is_leader']
                users.update_user(event.message.reply_message['from_id'], is_leader=not state)
                bot.api.send_chat_msg(event.chat_id, f"Установил статус лидера {not state}")
        return


class SetOfficer(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('офицер', 'officer'))
        self.set_access('creator')
        self.desc = 'Изменить роль лидера. Только для создателю'
        # self.set_active(False)
        return

    def run(self, bot: VkBot, event: VkBotEvent):
        if event.message.from_id == int(creator_id):
            if 'reply_message' in event.message.keys():
                state = users.get_user(event.message.reply_message['from_id'])['is_officer']
                users.update_user(event.message.reply_message['from_id'], is_officer=not state)
                bot.api.send_chat_msg(event.chat_id, f"Установил статус лидера {not state}")
        return
