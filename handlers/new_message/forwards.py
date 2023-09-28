import re
from typing import List, TYPE_CHECKING
import datetime

from utils.parsers import get_siege

from config import GUILD_CHAT_ID, DISCOUNT_PERCENT, creator_id
import utils.math
from dictionaries.emoji import item, gold, empty, flag
from utils import parsers
from utils.formatters import translate
from utils.words import frequent_letter
import profile_api

from ORM import session, UserInfo, Item, Logs, Task

if TYPE_CHECKING:
    from vk_bot.vk_bot import VkBot
    from vk_api.bot_longpoll import VkBotEvent


def forward_parse(self: "VkBot", event: "VkBotEvent"):
    fwd_txt = str(event.message.fwd_messages[0]['text']).encode('cp1251', 'xmlcharrefreplace').decode('cp1251')

    # if 'выловили рыбу' in fwd_txt:
    #     Logs(event.message.from_id, 'Fishing', on_message=event.message.fwd_messages[0]['text']).make_record()
    #     # TODO: make def for it
    #     return

    # if 'обыск руин' in fwd_txt:
    #     Logs(event.message.from_id, 'Ruins', on_message=event.message.fwd_messages[0]['text']).make_record()
    #     # TODO: make def for it
    #     return

    if 'заданий больше не осталось' in fwd_txt:
        Logs(event.message.from_id, 'guild_task_remind', on_message=event.message.fwd_messages[0]['text']).make_record()
        # TODO: make def for it
        return

    if fwd_txt.startswith(f'{item}1*'):
        Logs(event.message.from_id, 'Dark_vendor', on_message=event.message.fwd_messages[0]['text']).make_record()
        dark_vendor(self, event)
        return

    if 'присоединились к осадному лагерю' in fwd_txt:
        Logs(event.message.from_id, 'Siege',
             on_message='\n'.join([msg['text'] for msg in event.message.fwd_messages])).make_record()
        siege_report(self, event)
        return

    if 'обменяли элитные трофеи' in fwd_txt:
        Logs(event.message.from_id, 'Elites', on_message=event.message.fwd_messages[0]['text']).make_record()
        elites_response(self, event)
        return

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

    if 'Книгу целиком уже не спасти' in translate(fwd_txt):
        Logs(event.message.from_id, 'Book', on_message=event.message.fwd_messages[0]['text']).make_record()
        book_pages(self, event)
        return

    if 'Осталось выбрать, какому направлению последовать...' in fwd_txt:
        Logs(event.message.from_id, 'Cross', on_message=event.message.fwd_messages[0]['text']).make_record()
        cross_road(self, event)
        return

    else:
        Logs(event.message.from_id, 'other', on_message=fwd_txt.replace('\n', ' | '))

    return


def dark_vendor(self: "VkBot", event: "VkBotEvent"):
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
    DB.close()
    return


def symbol_guesser(self: "VkBot", event: "VkBotEvent"):
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


def travel_check(self: "VkBot", event: "VkBotEvent"):
    from dictionaries.puzzle_answers import travel_danger_list, travel_safe_list, travel_warn_list

    fwd_txt = str(event.message.fwd_messages[0]['text']).encode('cp1251', 'xmlcharrefreplace').decode('cp1251')
    fwd_txt = translate(fwd_txt)
    txt = fwd_txt.split('\n')[-1]

    if txt in travel_safe_list:
        answer = f"(+1) Можно продолжать путешествие"
    elif txt in travel_warn_list:
        answer = f"(+2) Можно продолжать путешествие"
    elif txt in travel_danger_list:
        answer = f"(+3) Событие предшествует смертельному!"
    else:
        answer = f"(+?) Неизвестное событие, сообщите в полигон или [id{creator_id}|ему]"

    self.api.send_chat_msg(event.chat_id, answer)
    return


def door_solver(self: "VkBot", event: "VkBotEvent"):
    from dictionaries.puzzle_answers import door_answers

    fwd_txt = str(event.message.fwd_messages[0]['text']).encode('cp1251', 'xmlcharrefreplace').decode('cp1251')
    fwd_txt = translate(fwd_txt)

    for answer in door_answers:
        if answer in fwd_txt:
            self.api.send_chat_msg(event.chat_id, 'Открываем дверь, а там ответ: ' + door_answers[answer])
            return

    self.api.send_chat_msg(event.chat_id, f"Ой, а я не знаю ответ\nCообщите в полигон или [id{creator_id}|ему]")
    return


def book_pages(self: "VkBot", event: "VkBotEvent"):
    from dictionaries.puzzle_answers import book_pages

    fwd_txt = str(event.message.fwd_messages[0]['text']).encode('cp1251', 'xmlcharrefreplace').decode('cp1251')
    fwd_txt = translate(fwd_txt)

    for puzzle in book_pages:
        if puzzle in fwd_txt:
            self.api.send_chat_msg(event.chat_id, 'Это страница из книги ' + book_pages[puzzle])
            return

    self.api.send_chat_msg(event.chat_id, f"Ой, а я не знаю ответ\nCообщите в полигон или [id{creator_id}|ему]")

    return


def elites_response(self: "VkBot", event: "VkBotEvent"):
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
    s.close()
    msg = f"Добавил {count} к элитным трофеям! Сдано за месяц: {user.elites_count}\n"
    msg += f"Осталось сдать {limit - user.elites_count} штук" \
        if limit > user.elites_count \
        else f"Сданы все необходимые трофеи"
    self.api.send_chat_msg(event.chat_id, msg)

    # TODO: logs in chat for logs
    return


def siege_report(self: "VkBot", event: "VkBotEvent"):
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
    s.close()
    msg = f"Зарегистрировал твое участие в осаде за {data['name']}"
    self.api.send_chat_msg(event.chat_id, msg)

    # TODO: logs in chat for logs
    return


def cross_road(self: "VkBot", event: "VkBotEvent"):
    fwd_txt = str(event.message.fwd_messages[0]['text']).encode('cp1251', 'xmlcharrefreplace').decode('cp1251')
    fwd_txt = translate(fwd_txt)

    west, north, east = (parsers.parse_cross_signs(i) for i in fwd_txt.split('\n') if flag in i)
    msg = "Направления ведут к\n"
    msg += f"{flag} Запад - Это {west}\n"
    msg += f"{flag} Север - Это {north}\n"
    msg += f"{flag} Восток - Это {east}\n"

    self.api.send_chat_msg(event.chat_id, msg)

    return


def task_reminder(self: "VkBot", event: "VkBotEvent"):
    return


def fishing(self: "VkBot", event: "VkBotEvent"):
    return


def ruins(self: "VkBot", event: "VkBotEvent"):
    return
