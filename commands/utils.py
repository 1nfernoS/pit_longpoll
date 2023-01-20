from commands import Command

from config import creator_id, GUILD_CHAT_ID, GUILD_NAME

from utils.emoji import level, strength, agility, endurance, luck, attack, defence

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
        self.set_active(False)
        return

    def run(self, bot: VkBot, event: VkBotEvent):
        if event.message.from_id not in bot.api.get_members(GUILD_CHAT_ID):
            war_list = f'Нет, это только для членов гильдии {GUILD_NAME}!'
        else:
            # f"1. Имя Фамилия (расы - класс): &#128481;{attack} &#128737;{defence} &#128074;{strength} &#128400;{agility} &#10084;{endurance} &#127808;{luck}" \
            war_list = "У нас сейчас нет войны с кем-либо!"
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
                       f"{attack}:{attack} {defence}:{defence} {luck}:{luck}\n" \
                       f"{strength}:{strength} {agility}:{agility} {endurance}:{endurance}\n"
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


class Bill(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('налоговая',))
        self.set_access('creator')
        self.desc = 'Списать налог с баланса. Только для создателя'
        # self.set_active(False)
        return

    def run(self, bot: VkBot, event: VkBotEvent):
        if event.message.from_id == int(creator_id):
            from utils.scripts import withdraw_bill
            withdraw_bill(bot)
            bot.api.send_chat_msg(event.chat_id, f"Списал налог с баланса, проверять можно командой баланс")

        return


class NewYear(Command):
    __CONGRATS = {
        205486328: '[id205486328|Антон], первый год на лидерке, и благодаря вам с Леной я появился на свет! '
                   'Несмотря на все мои затупливания, вы продолжали подкармливать меня и уговаривали терпеть '
                   'этого ужасного кодера! Надеюсь в наступающем году мы станем главной ги, и я наконец всех съем! Ням :3',
        166287013: '[id166287013|Денис], я рад что ты справлялся с библиотекой без меня и я рад, что до сих пор '
                   'помогаешь мне в бух учете, а то цены я еще освоился, а следить у кого там что и как я так и не '
                   'понял... Но научусь! Так что и ты развивайся в наступающем году, мур :3',
        270672839: '[id270672839|Екатерина], ой ой ой, а я помню тебя! Ты тот апостол что игралась со мной и '
                   'писала мне, это было очень мило с твоей стороны) Надеюсь ты продолжишь путь с нами а я буду '
                   'мурчать на ушко, как научусь не только писать, но и говорить :3',
        339727110: '[id339727110|Павел], хотя я и вижу тебя нечасто, ты помогал моей второй личности делать '
                   'полезные вещи, которые до сих пор помогают нам! Для меня все эти апостольные религиозные '
                   'штуки пока сложны, но думаю когда-нибудь и это сумею сам, но ты тоже не пропадай тогда в '
                   'следующем году :3',
        16914430: '[id16914430|Елена], о, лидерам гильдии тоже интересно что за пожелания я приготовил? Я рад, '
                  'что мы за столь короткий срок достигли просто отличных результатов, и я надеюсь мы продолжим '
                  'развивать наше безбашенное местечко >:3',
        158154503: '[id158154503|Миша], еще и поздравлять тебя?! Обойдешься, в следующий раз посмотрим',
        211500453: '[id211500453|Женя], я может постоянно игнорирую тебя как члена гильдии, но мне так сказали, '
                   'я ничего не могу поделать с этим!! Но тем не менее, ты очень активно участвовуешь в нашей '
                   'жизни и надеюсь что это продолжиться - мы создадим альянс и захватим ВЕСЬ КОЛОДЕЦ МУХАХА... '
                   'Ой, то есть с наступающим)',
        323010256: '[id323010256|Сергей], уж не знаю чего вы там с Виталей не делите вечно, но все равно круто, '
                   'что продожаешь расти с нами! Жду на вершине топов :3',
        187423112: '[id187423112|Виталий], уж не знаю чего вы там с Сережей не делите вечно, но все равно круто, '
                   'что продожаешь расти с нами! Жду на вершине топов :3\nИ просто с наступающим)',
        249850514: '[id249850514|Егор] о твоей удачи можно легенды слагать, так что держи медальку как миллионный '
                   'посетитель нашего сай... \n'
                   'Так, это что-то не то, с наступающим, и чтобы удача растекалась рекой!',
        152716092: '[id152716092|Димон], я лично тебя не так часто видел, но я рад что ты с нами! Надеюсь успехи '
                   'будут сопутствовать весь год!',
        1252214: '[id1252214|Иван], ты только не удивляйся что я говорю так, я больше не буду. Но спасибо что '
                 'подкармливаешь меня, скоро я смогу поработить мир и вывести ги на новый уровень!',
        60280841: '[id60280841|Алексей], давно не видел тебя в колодце, заходи! Как раз Новый Год отпразднуем)',
        53469892: '[id53469892|Игнатий], позитивные и деловые люди это прекрасно! Надеюсь меня обучат выпивать и '
                  'я смогу составить компанию на новый год полноценно :3',
        30146111: '[id30146111|Рамиль], я скучаю по твоим инфографикам... Приходи праздновать, и оставайся на годик!',
        303191196: '[id303191196|Илья], рад, что ты с нами! И я надеюсь что это взаимно и главное надолго - люблю '
                   'смотреть на растущие цифорки в течении года :3',
        19184951: '[id19184951|Андрей], заходи в гости почаще! Мы пока набираем обороты, и еще не поздно прийти, '
                  'пока еще не захватили весь колодец и не подчинили все и вся! Шучу, тебе всегда рады, и с новым Годом)',
        452968833: '[id452968833|Кира], жду не дождусь вас с Андреем в гости! Нам ведь еще мир захватывать) '
                   'А пока с Новым Годом, мур :3',
        16191014: '[id16191014|Юрий], Активная игра - залог успеха по захвату колодца! Рад что ты с нами, и '
                  'надеюсь это взаимно! С наступающим!',
        56042272: '[id56042272|Иршат], с теплыми штанишками тебя! И чтобы весь год зад был в тепле а враги в крови!',
        134458209: '[id134458209|Серафим], уже почти 2 месяца с нами, и это прекрасно! Вот захвачу колодец, '
                   'поставлю тебя каким-нибудь министром. Ты главное сам расти, а то неловко получится, а пока с наступающим :3',
        539841441: '[id539841441|Дмитрий], я пока не так много знаю про тебя, но все равно здорово, что ты с '
                   'нами! Потому что кто не с нами, тот... Скорее всего наш союзник, раз еще живой. не стесняйся '
                   'общаться, и успехов в наступающем году!'
    }

    __DEFAULTS = [
        '3-е января.... день прощания, ой, каникульный день, конечно же',
        'С новым годом? Прям с Новым? И правда... С наступающим!',
        'нг',
        'О, вы вызвали 1 штук нг!\nС новым годом!',
        '&#10024; Наложено новогоднее настроение.',
        'Я не проснулся)',
        'Я спать, Новый год все таки',
        'Читаю профиль... Проверяю торговца... Выбираю поздравление с наступающим...',
        'Ой, а я не знаю даже как реагировать, попробуй еще раз',
        'Кинуть_снежок',
        ')0))0)))0)))0)00)00)0',
        'А вот не с Новым Годом, а с наступающим!',
        'А вот не с наступающим, а с Новым годом!',
        'С Новым Годом!!!',
        'С Новым Годом!!',
        'Интересно, а если год не сдавать профиль... Не делайте так, с новым годом)',
        'Говорят, что в лагах колодца виноват не вк... С Новым годом',
        '...ставляем сюда игрек, получаем, что прошло 3 дня и -485 часов... Что-то не то...',
        'С наступающим!!!',
        'С наступающим!!',
        'Мне тут отшельник нашептал, что скоро год закончится, это правда? А куда он денется?...',
        'И правда, уже конец года, надо бы подарки купить...',
        'Это не индивидуальное поздравление',
        'Вы думаете это Новый Год? на самом деле это был я, котя! :3',
        'Снять 36000, добавить 15042... на счету минус можжевельник... Простите, увлекся подсчетом, с новым Годом)'
    ]
    def __init__(self):
        from datetime import date
        super().__init__(__class__.__name__, ('нг',))
        self.set_access('all')
        self.desc = 'Новогодние поздравления, доступны членам гильдии и всем всем всем!'

        d = date.today()
        self.set_active(date(d.year, 12, 25) < d < date(d.year+1, 1, 5))
        return

    def run(self, bot: VkBot, event: VkBotEvent):
        congratulation = self.__get_congratulation(event.message.from_id)
        bot.api.send_chat_msg(event.chat_id, congratulation)
        return

    def __get_congratulation(self, id_vk):
        import random

        return self.__CONGRATS.pop(id_vk) if id_vk in self.__CONGRATS.keys() else random.choice(self.__DEFAULTS)
