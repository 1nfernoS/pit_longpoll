import re
from typing import List
import datetime

from vk_api.bot_longpoll import VkBotEvent

from utils.parsers import get_siege
from vk_bot.vk_bot import VkBot

from config import GUILD_CHAT_ID, DISCOUNT_PERCENT, creator_id
import utils.math
from dictionaries.emoji import item, gold, empty
from utils import parsers
from utils.formatters import translate
from utils.words import frequent_letter
import profile_api

from ORM import session, UserInfo, Item, Logs


def forward_parse(self: VkBot, event: VkBotEvent):
    fwd_txt = str(event.message.fwd_messages[0]['text']).encode('cp1251', 'xmlcharrefreplace').decode('cp1251')
    if fwd_txt.startswith(f'{item}1*'):
        Logs(event.message.from_id, 'Dark_vendor', on_message=event.message.fwd_messages[0]['text']).make_record()
        dark_vendor(self, event)
        return

    if 'присоединились к осадному лагерю' in fwd_txt:
        Logs(event.message.from_id, 'Siege', on_message='\n'.join([msg['text'] for msg in event.message.fwd_messages])).make_record()
        siege_report(self, event)
        pass

    if 'обменяли элитные трофеи' in fwd_txt:
        Logs(event.message.from_id, 'Elites', on_message=event.message.fwd_messages[0]['text']).make_record()
        elites_response(self, event)
        pass

    if 'Символы' in fwd_txt:
        Logs(event.message.from_id, 'Symbols', on_message=event.message.fwd_messages[0]['text']).make_record()
        symbol_guesser(self, event)
        return

    if 'Путешествие продолжается...' in fwd_txt:
        Logs(event.message.from_id, 'Travel', on_message=event.message.fwd_messages[0]['text']).make_record()
        travel_check(self, event)
        return

    if fwd_txt.startswith('Дверь с грохотом открывается'):
        Logs(event.message.from_id, 'Door', on_message=event.message.fwd_messages[0]['text']).make_record()
        door_solver(self, event)
        return

    if fwd_txt.startswith('Книгу целиком уже не спасти'):
        Logs(event.message.from_id, 'Book', on_message=event.message.fwd_messages[0]['text']).make_record()
        book_pages(self, event)
        return

    else:
        Logs(event.message.from_id, 'other\t' + fwd_txt.replace('\n', ' | '))

    return


def dark_vendor(self: VkBot, event: VkBotEvent):
    fwd_txt = str(event.message.fwd_messages[0]['text']).encode('cp1251', 'xmlcharrefreplace').decode('cp1251')
    msg_id = self.api.send_chat_msg(event.chat_id, 'Проверяю торговца...')[0]
    fwd_split = fwd_txt.split('\n')
    item_name = fwd_split[0][11:]
    item_price = int(re.findall(r'\d+', fwd_split[1][9:])[0])

    DB = session()
    item_: Item = DB.query(Item).filter(Item.item_name.ilike(f"{item_name}%"), Item.item_has_price == 1).first()
    if not item_:
        msg = 'Кажется, такой предмет не продается на аукционе'
        self.api.edit_msg(msg_id['peer_id'], msg_id['conversation_message_id'], msg)
        return

    auc_price = profile_api.price(item_.item_id)
    commission_price = utils.math.commission_price(item_price)

    if auc_price > 0:
        guild_price = utils.math.discount_price(auc_price)
        guild_commission_price = utils.math.commission_price(guild_price)

        msg = f'Товар: {item}{item_name}\nЦена торговца: {gold}{item_price} ' \
              f'({gold}{commission_price})' + \
              f'\nЦена аукциона: {gold}{auc_price} (со скидкой гильдии {DISCOUNT_PERCENT}%: ' \
              f'{gold}{guild_price}' \
              f'({gold}{guild_commission_price})\n\n'

        if event.chat_id == GUILD_CHAT_ID:
            if item_name.startswith('Книга - ') and item_.item_users:
                guild_roles = (0, 1, 2, 3, 4, 5, 6)
                in_equip: List[UserInfo] = item_.item_users
                msg += f'{item}В экипировке у ' \
                       f'{self.api.get_names([i.user_id for i in in_equip if i.user_role.role_id in guild_roles])}'
    else:
        msg = f'Товар: {item}{item_name}\nЦена торговца: {gold}{item_price} ({gold}{commission_price})' + \
              f'\nВот только... Он не продается, Сам не знаю почему'

    self.api.edit_msg(msg_id['peer_id'], msg_id['conversation_message_id'], msg)
    return


def symbol_guesser(self: VkBot, event: VkBotEvent):
    fwd_txt = str(event.message.fwd_messages[0]['text']).encode('cp1251', 'xmlcharrefreplace').decode('cp1251')

    if empty not in fwd_txt.split('\n')[1]:
        return

    msg_id = self.api.send_chat_msg(event.chat_id, 'Символы... Символы... Сейчас вспомню')[0]
    res_list = parsers.guesser(fwd_txt)
    best_guess = frequent_letter(res_list)
    if res_list:
        if not fwd_txt.split('\n')[1].replace(empty, '').replace(' ', ''):
            msg = f'Ну так не интересно! Попробуй букву {best_guess.upper()}\n'
        else:
            msg = 'Ну точно! Это наверняка что-то из этого:\n'
            msg += '\n'.join(res_list)
    else:
        msg = 'Что-то не пойму, что это может быть'
    self.api.edit_msg(msg_id['peer_id'], msg_id['conversation_message_id'], msg)
    return


def travel_check(self: VkBot, event: VkBotEvent):
    _safe_list = ('Впереди все спокойно.', 'Впереди не видно никаких препятствий.', 'Время пересечь мост через реку.',
                  'Вы бодры как никогда.', 'Густые деревья шумят на ветру.', 'Густые заросли травы по правую руку.',
                  'Дорога ведет прямиком к приключениям.', 'Дорога проходит мимо озера.', 'Идти легко, как никогда.',
                  'На небе ни единого облачка.', 'Не время останавливаться!', 'Ничего не предвещает беды.',
                  'Нужно двигаться дальше.', 'От широкой дороги ветвится небольшая тропинка.',
                  'Пение птиц доносится из соседнего леса.', 'Погода просто отличная.',
                  'Самое время найти еще что-то интересное.', 'Солнечная поляна виднеется впереди.',
                  'Стрекот сверчков заглушает другие звуки.', 'Только вперед!', 'Тропа ведет в густой лес.')

    _warn_list = ('Вас клонит в сон от усталости...', 'Возможно, стоит повернуть назад?..',
                  'Вдалеке слышны страшные крики...', 'Местность становится все опаснее и опаснее...',
                  'Нужно быть предельно осторожным...', 'Нужно ли продолжать путь...',
                  'Опасность может таиться за каждым деревом...', 'Путь становится все труднее...',
                  'С каждым шагом чувство тревоги нарастает...', 'Становится сложно разглядеть дорогу впереди...',
                  'Сердце громко стучит в груди...', 'Туман начинает сгущаться...', 'Тучи сгущаются над дорогой...')

    _danger_list = ('Боль разрывает Вас на части...', 'В воздухе витает отчетливый запах смерти...',
                    'Воздух просто гудит от опасности...', 'Вы уже на пределе...',
                    'Еще немного, и Вы падаете без сил...', 'Кажется, конец близок...',
                    'Крик отчаяния вырывается у Вас из груди...', 'Ноги дрожат от предчувствия беды...',
                    'Нужно бежать отсюда!', 'Силы быстро Вас покидают...', 'Смерть таится за каждым поворотом...',
                    'Чувство тревоги бьет в колокол!', 'Кажется, конец близок...',
                    'Еще немного, и Вы падете без сил...')

    fwd_txt = str(event.message.fwd_messages[0]['text']).encode('cp1251', 'xmlcharrefreplace').decode('cp1251')
    fwd_txt = translate(fwd_txt)
    txt = fwd_txt.split('\n')[-1]

    if txt in _safe_list:
        answer = f"(+1) Можно продолжать путешествие"
    elif txt in _warn_list:
        answer = f"(+2) Можно продолжать путешествие"
    elif txt in _danger_list:
        answer = f"(+3) Событие предшествует смертельному!"
    else:
        answer = f"(+?) Неизвестное событие, сообщите в полигон или [id{creator_id}|ему]"

    self.api.send_chat_msg(event.chat_id, answer)
    return


def door_solver(self: VkBot, event: VkBotEvent):
    _answers = {
        'Похоже, нужно поставить фигурку на определенный участок карты...': 'Темнолесье',
        'Итак, как же звали воина...': 'Гер, Натаниэль, Эмбер',
        'Видимо, этот камень нужно вложить в одну из вытянутых рук.': 'Человек',
        'В груди моей горел пожар, но сжег меня дотла. Ты имя назови мое, и получи сполна...': 'Роза',
        'Итак, эльфа нужно расположить...': 'Северо-восток, Северо-запад, Юг материка',
        'Сяэпьчео рущэр': 'Берем строку, прогоняем по шифру Цезаря... \nЛадно, это "Гробница веков"',
        'Начнем с юркого гоблина...': 'Разрезать мечом, Ударить молотом, Уколоть кинжалом',
        'Видимо, порядок этих барельефов как-то связан с рычагами...': 'Грах, Ева, Трор, Смотритель',
        'Итак, главным реагентом добавим...': 'Пещерный корень, Первозданная вода, Рыбий жир',
        'КАКОВ ЦВЕТ СЕРДЦА?': 'Фиолетовый',
        'Где в настоящее время находится истинный спуск на путь к Сердцу Глубин?': 'Темнолесье',
        'Возможно, нужно что-то произнести? Или нет?..': 'Уйти. Да, просто уйти',
        'В каком же порядке активировать плиты?..': 'Осень, Зима, Весна, Лето'
    }

    fwd_txt = str(event.message.fwd_messages[0]['text']).encode('cp1251', 'xmlcharrefreplace').decode('cp1251')
    fwd_txt = translate(fwd_txt)

    for answer in _answers:
        if answer in fwd_txt:
            self.api.send_chat_msg(event.chat_id, 'Открываем дверь, а там ответ: ' + _answers[answer])
            return

    self.api.send_chat_msg(event.chat_id, f"Ой, а я не знаю ответ\nCообщите в полигон или [id{creator_id}|ему]")
    return


def book_pages(self: VkBot, event: VkBotEvent):
    _answers = {
        'только в неожиданный момент, свободной от оружия рукой, в незащищенную зону': 'Грязный удар',
        'эти бойцы не носили, однако это позволяло полностью сосредоточиться на агрессии в бою, имея': 'Гладиатор',
        'даже, казалось бы, всего одно умение, но именно оно может стать серьезным козырем': 'Инициативность',
        'использовать особые пластины в доспехе, чтобы прикрыть эти места': 'Прочность ',
        'самое эффективное из них, позволяющее ослабить противника прямо во время': 'Проклятие тьмы',
        'не брезговать осмотреть каждый карман, даже если с первого взгляда кажется, что': 'Мародер',
        'обитают ближе ко дну, чаще скрываясь в водорослях': 'Рыбак',
        'истинный путь, в зависимости от совершенных деяний и поступков': 'Воздаяние',
        'более важен размах, который усилит тяжесть удара и позволит пробить': 'Дробящий удар',
        'выследить их можно по особым магическим знакам, которые оставляют только хранители': 'Охотник за головами',
        'главное - точно соблюдать время между ними, и тогда появится возможность повторного': 'Расчётливость ',
        'поможет сэкономить время при перевязке, уменьшив': 'Быстрое восстановление',
        'если они небольшие - затянутся сами собой, даже в бою, не требуя дополнительного лечения': 'Регенерация',
        'такую позу, которая максимально подчеркнет опасность': 'Устрашение',
        'падал, но снова вставал, продолжая путь к своей цели': 'Упорность',
        'не столько длина пореза, сколько его глубина': 'Кровотечение',
        'своевременно и быстро совершенное - может спасти жизнь от любого, даже смертельного удара': 'Подвижность',
        'использовать собственный факел даже в том случае, если вокруг нет ни единого другого источника': 'Огонек надежды',
        'иногда важнее, чем атака. Переждав несколько ударов, можно восстановить': 'Защитная стойка',
        'но не стоит страшиться - ведь Вам, в отличие от противника, он не причинит вреда, а наоборот': 'Целебный огонь',
        'если связывать их в одну охапку, то они займут меньше места в': 'Запасливость',
        'и пусть эти приметы и не всегда будут полезны, но в случае, когда': 'Суеверность',
        'прямой удар острием вперед. Лезвие должно войти достаточно': 'Колющий удар',
        'грязь под ногами, как самый простой вариант. Цельтесь в глаза, чтобы': 'Слепота',
        'позволит быстро откупорить крышку и одним глотком осушить': 'Водохлеб',
        'нанести удар вдоль, максимально сблизившись с противником, чтобы он точно не смог': 'Режущий удар',
        'следить за каждым движением, которое может оказаться врагом, меньше обращая внимания на окружающее': 'Бесстрашие',
        'отрешившись от внешнего мира, однако при этом не надейтесь избежать': 'Стойка сосредоточения',
        'резким взмахом, едва задевая самым острием по широкому': 'Рассечение',
        'в сочленение между пластинами, и только тогда они': 'Раскол',
        'не обязательно настроены агрессивно, многих из них можно обойти просто': 'Исследователь',
        'проникает в саму кровь врага, отравляя ее и не позволяя': 'Заражение',
        'убедиться, что вокруг нет ни единого источника света, и собрать вокруг': 'Сила теней',
        'переродиться из пепла, но только в том случае, если': 'Феникс',
        'будет достигнут только если противник находится при смерти, и уже не может': 'Расправа',
        'не подставляя свои слабые точки под вероятную траекторию': 'Неуязвимый',
        'жизненные силы вокруг себя и направить их поток в свое тело': 'Слабое исцеление',
        'не только следить за всем, происходящим вокруг, но и не забывать о собственных карманах': 'Внимательность',
        'и всю накопленную за это время силу высвободить в одном': 'Мощный удар',
        'и кровь, заливающая глаза, придаст силы и ярости для одного': 'Берсеркер',
        'очистить разум от посторонних мыслей, сосредоточившись на': 'Непоколебимый',
        'вонзить в плоть, незащищенную броней. Лучшей точкой является шея, если': 'Удар вампира',
        'резкий и громкий звук, который собьет концентрацию противника': 'Ошеломление',
        'позволит быстрее перетаскивать камни, разбирая обвалившийся участок': 'Расторопность',
        'не всегда ценность находки может быть видна сразу, иногда приходится': 'Собиратель',
        'и если провести удар прямо в этот момент, то противник попросту не успеет': 'Контратака',
        'спасительной жидкостью, которая, иногда, является полезнее любого заклинания': 'Ведьмак',
        'впитывать знания в любой ситуации, совершенствуя свои': 'Ученик',
        'дополнительный вес, придающий силу удара вместе с разгоном': 'Таран',
        'разрезать вдоль, аккуратно поддев ножом внутреннюю часть': 'Браконьер',
        'зарисовать на бумаге, каждый поворот, каждую': 'Картограф',
        'выверенные движения позволят снять пробку быстрее и сократить время': 'Ловкость рук',
        'в нужный момент подставить свой клинок под удар, отведя': 'Парирование',
        'пригнувшись максимально мягко ступая по каменному': 'Незаметность',
        'правильно напрягая мышцы, чтобы позволить им': 'Атлетика',
        'иммунитет организма, таким образом отравление не сможет': 'Устойчивость'
    }

    fwd_txt = str(event.message.fwd_messages[0]['text']).encode('cp1251', 'xmlcharrefreplace').decode('cp1251')
    fwd_txt = translate(fwd_txt)

    for answer in _answers:
        if answer in fwd_txt:
            self.api.send_chat_msg(event.chat_id, 'Это страница из книги ' + _answers[answer])
            return

    self.api.send_chat_msg(event.chat_id, f"Ой, а я не знаю ответ\nCообщите в полигон или [id{creator_id}|ему]")

    return


def elites_response(self: VkBot, event: VkBotEvent):
    fwd_txt = str(event.message.fwd_messages[0]['text']).encode('cp1251', 'xmlcharrefreplace').decode('cp1251')
    date = datetime.datetime.fromtimestamp(event.message.fwd_messages[0]['date'])
    now = datetime.datetime.now(tz=None)

    s = session()
    user: UserInfo = s.query(UserInfo).filter(UserInfo.user_id == event.message.from_id).first()

    if not user:
        return

    if user.user_role.role_id in (7, 8, 9):
        return

    if date.date() != now.date():
        self.api.send_chat_msg(event.chat_id, 'Мне нужны элитные трофеи сданные лишь сегодня')
        return

    if user.user_stats.user_level < 100:
        limit = 40
    elif user.user_stats.user_level < 250:
        limit = 90
    else:
        limit = 120

    count = parsers.get_elites(fwd_txt)

    user.elites_count += count
    s.add(user)
    s.commit()
    msg = f"Добавил {count} к элитным трофеям! Сдано за месяц: {user.elites_count}\n"
    msg += f"Осталось сдать {limit - user.elites_count} штук" \
        if limit > user.elites_count \
        else f"Сданы все необходимые трофеи"
    self.api.send_chat_msg(event.chat_id, msg)

    # TODO: logs in chat for logs
    return


def siege_report(self: VkBot, event: VkBotEvent):
    fwd_txt = str(event.message.fwd_messages[0]['text']).encode('cp1251', 'xmlcharrefreplace').decode('cp1251')
    date = datetime.datetime.fromtimestamp(event.message.fwd_messages[0]['date'])
    now = datetime.datetime.now(tz=None)

    s = session()
    user: UserInfo = s.query(UserInfo).filter(UserInfo.user_id == event.message.from_id).first()

    if not user:
        return

    if user.user_role.role_id in (7, 8, 9):
        return

    if date.date() != now.date():
        self.api.send_chat_msg(event.chat_id, 'Я не принимаю отчеты по осаде за другие дни')
        # return

    data = get_siege(fwd_txt)

    user.siege_flag = True
    s.add(user)
    s.commit()
    msg = f"Зарегистрировал твое участие в осаде за {data['name']}"
    self.api.send_chat_msg(event.chat_id, msg)

    # TODO: logs in chat for logs
    return
