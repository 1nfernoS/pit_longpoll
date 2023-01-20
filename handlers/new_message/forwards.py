import re

from vk_api.bot_longpoll import VkBotEvent

from vk_bot.vk_bot import VkBot

from config import GUILD_CHAT_ID, DISCOUNT_PERCENT
import utils.math
from utils.emoji import item_emoji, gold_emoji, empty
from utils import parsers
import profile_api

from DB.items import get_item_by_name
from DB.users import get_equip

from logger import get_logger

logger = get_logger(__name__, 'forwards')


def forward_parse(self: VkBot, event: VkBotEvent):
    fwd_txt = str(event.message.fwd_messages[0]['text']).encode('cp1251', 'xmlcharrefreplace').decode('cp1251')
    if fwd_txt.startswith(f'{item_emoji}1*'):
        logger.info('dark_vendor\t' + fwd_txt.replace('\n', ' | '))
        dark_vendor(self, event)
        return

    # TODO: move to utils.emoji
    if fwd_txt.startswith('&#9989;') and '&#128100;' in fwd_txt:
        logger.info('siege\t' + fwd_txt.replace('\n', ' | '))
        pass

    # 'обменяли элитные трофеи' in fwd_txt and
    # TODO: fix false reactions (trophies, PvP)
    if '&#127941;' in fwd_txt:
        logger.info('elites\t' + fwd_txt.replace('\n', ' | '))
        pass

    # TODO: fix false reactions (PvP)
    if empty in fwd_txt:
        logger.info('symbols\t' + fwd_txt.replace('\n', ' | '))
        symbol_guesser(self, event)
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
    try:
        item_id = get_item_by_name(item_name)
    except KeyError:
        msg = 'Кажется, такого предмета нет в базе'
        self.api.send_chat_msg(event.chat_id, msg)
        return

    auc_price = profile_api.price(item_id)

    in_equip = []
    for row in get_equip():
        if item_id in row[1]:
            in_equip.append(row[0])

    commission_price = utils.math.commission_price(item_price)

    if auc_price > 0:
        guild_price = utils.math.discount_price(auc_price)
        guild_commission_price = utils.math.commission_price(guild_price)

        msg = f'Товар: {item_emoji}{item_name}\nЦена торговца: {gold_emoji}{item_price} ' \
              f'({gold_emoji}{commission_price})' + \
              f'\nЦена аукциона: {gold_emoji}{auc_price} (со скидкой гильдии {DISCOUNT_PERCENT}%: ' \
              f'{gold_emoji}{guild_price}' \
              f'({gold_emoji}{guild_commission_price})\n\n'

        if int(event.chat_id) == GUILD_CHAT_ID:
            if item_name.startswith('Книга - '):
                if in_equip:
                    msg += f'{item_emoji}В экипировке у {self.api.get_names(in_equip)}'
    else:
        msg = f'Товар: {item_emoji}{item_name}\nЦена торговца: {gold_emoji}{item_price} ({gold_emoji}{commission_price})' + \
              f'\nВот только... Он не продается, Сам не знаю почему'

    self.api.edit_msg(msg_id['peer_id'], msg_id['conversation_message_id'], msg)
    return


def symbol_guesser(self: VkBot, event: VkBotEvent):
    fwd_txt = str(event.message.fwd_messages[0]['text']).encode('cp1251', 'xmlcharrefreplace').decode('cp1251')

    if not fwd_txt.split('\n')[1].replace(empty, '').replace(' ', ''):
        self.api.send_chat_msg(event.chat_id, 'Ну так не интересно, попробуй хотя бы одну букву сам')
        return

    if empty not in fwd_txt.split('\n')[1]:
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
