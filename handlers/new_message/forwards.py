import re
from typing import List

from vk_api.bot_longpoll import VkBotEvent

from vk_bot.vk_bot import VkBot

from config import GUILD_CHAT_ID, DISCOUNT_PERCENT, creator_id
import utils.math
from utils.emoji import item, gold, empty
from utils import parsers
from utils.formatters import translate
import profile_api

from ORM import session as DB
import ORM

from logger import get_logger

logger = get_logger(__name__, 'forwards')


def forward_parse(self: VkBot, event: VkBotEvent):
    fwd_txt = str(event.message.fwd_messages[0]['text']).encode('cp1251', 'xmlcharrefreplace').decode('cp1251')
    if fwd_txt.startswith(f'{item}1*'):
        logger.info('dark_vendor\t' + fwd_txt.replace('\n', ' | '))
        dark_vendor(self, event)
        return

    if 'присоединились к осадному лагерю' in fwd_txt:
        logger.info('siege\t' + fwd_txt.replace('\n', ' | '))
        pass

    if 'обменяли элитные трофеи' in fwd_txt:
        logger.info('elites\t' + fwd_txt.replace('\n', ' | '))
        pass

    if 'Символы' in fwd_txt:
        logger.info('symbols\t' + fwd_txt.replace('\n', ' | '))
        symbol_guesser(self, event)
        return

    if 'Путешествие продолжается...' in fwd_txt:
        travel_check(self, event)
        return

    if fwd_txt.startswith('Дверь с грохотом открывается'):
        door_solver(self, event)
        return


    else:
        logger.info('other\t' + fwd_txt.replace('\n', ' | '))
    # puzzles

    return


def dark_vendor(self: VkBot, event: VkBotEvent):
    fwd_txt = str(event.message.fwd_messages[0]['text']).encode('cp1251', 'xmlcharrefreplace').decode('cp1251')
    msg_id = self.api.send_chat_msg(event.chat_id, 'Проверяю торговца...')[0]
    fwd_split = fwd_txt.split('\n')
    item_name = fwd_split[0][11:]
    item_price = int(re.findall(r'\d+', fwd_split[1][9:])[0])
    item_: ORM.Item = DB.query(ORM.Item).filter(ORM.Item.item_name.ilike(f"{item_name}%"),
                                               ORM.Item.item_has_price == 1).first()
    if not item_:
        msg = 'Кажется, такого предмета нет в базе'
        self.api.send_chat_msg(event.chat_id, msg)
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

        if int(event.chat_id) == GUILD_CHAT_ID:
            if item_name.startswith('Книга - ') and item_.item_users:
                in_equip: List[ORM.UserInfo] = item_.item_users
                msg += f'{item}В экипировке у {self.api.get_names([i.user_id for i in in_equip])}'
    else:
        msg = f'Товар: {item}{item_name}\nЦена торговца: {gold}{item_price} ({gold}{commission_price})' + \
              f'\nВот только... Он не продается, Сам не знаю почему'

    self.api.edit_msg(msg_id['peer_id'], msg_id['conversation_message_id'], msg)
    return


def symbol_guesser(self: VkBot, event: VkBotEvent):
    fwd_txt = str(event.message.fwd_messages[0]['text']).encode('cp1251', 'xmlcharrefreplace').decode('cp1251')

    if empty not in fwd_txt.split('\n')[1]:
        return

    if not fwd_txt.split('\n')[1].replace(empty, '').replace(' ', ''):
        self.api.send_chat_msg(event.chat_id, 'Ну так не интересно, попробуй хотя бы одну букву сам')
        return

    msg_id = self.api.send_chat_msg(event.chat_id, 'Символы... Символы... Сейчас вспомню')[0]
    res_list = parsers.guesser(fwd_txt)
    if res_list:
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
                    'Чувство тревоги бьет в колокол!', 'Кажeтся, кoнец близок...')

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
