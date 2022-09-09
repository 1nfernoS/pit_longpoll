import re

from vk_api.bot_longpoll import VkBotEvent

from vk_bot.vk_bot import VkBot

from config import GUILD_CHAT_ID

import profile_api

from DB.items import get_item_by_name
from DB.users import get_equip


def forward_parse(self: VkBot, event: VkBotEvent):

    item_emoji = '&#128093;'
    gold_emoji = '&#127765;'

    fwd_txt = str(event.message.fwd_messages[0]['text']).encode('cp1251', 'xmlcharrefreplace').decode('cp1251')
    if fwd_txt.startswith(item_emoji+'1*'):
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

        if auc_price > 0:
            msg = f'Товар: {item_emoji}{item_name}\nЦена торговца: {gold_emoji}{item_price} ({gold_emoji}{round(item_price/0.9)})' + \
                  f'\nЦена аукциона: {gold_emoji}{auc_price} (со скидкой гильдии 30%: {gold_emoji}{round(auc_price*0.7)}({gold_emoji}{round(auc_price*0.7/0.9)})\n\n'

            if int(event.chat_id) == GUILD_CHAT_ID:
                if item_name.startswith('Книга - '):
                    if in_equip:
                        msg += f'{item_emoji}В экипировке у {self.api.get_names(in_equip)}'
        else:
            msg = f'Товар: {item_emoji}{item_name}\nЦена торговца: {gold_emoji}{item_price} ({gold_emoji}{round(item_price/0.9)})' + \
                  f'\nВот только... Он не продается, Сам не знаю почему'

        self.api.send_chat_msg(event.chat_id, msg)

    return
