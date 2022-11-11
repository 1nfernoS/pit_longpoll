# builtins
import re
from datetime import datetime
import logging
import time

# requirement's import
from vk_api.bot_longpoll import VkBotEvent

# config and packages
from config import GUILD_NAME, GUILD_CHAT_ID, COMMISSION_PERCENT

import DB.users as users
import DB.user_data as user_data

from utils.parsers import parse_profile, parse_storage_action
from utils.formatters import str_datetime, datediff

from logger import get_logger

# import for typing hints
from vk_bot.vk_bot import VkBot

logger = get_logger(__name__, 'group_messages')


def bot_message(self: VkBot, event: VkBotEvent):
    # group's message in chat

    if "Ваш профиль:" in event.message.text:
        logger.info('Profile\t'+event.message.text.encode('cp1251', 'xmlcharrefreplace').decode('cp1251').replace('\n', ' | '))
        msg_id = self.api.send_chat_msg(event.chat_id, 'Читаю профиль...')[0]
        answer = profile_message(self, event)
        photo = ''
        if event.chat_id == GUILD_CHAT_ID:
            if event.message['attachments']:
                if 'photo' in event.message['attachments'][0]:
                    at = event.message['attachments'][0]
                    photo = f"photo{at['photo']['owner_id']}_{at['photo']['id']}_{at['photo']['access_key']}"
            msg_id_del = self.api.get_conversation_msg(event.message.peer_id, event.message.conversation_message_id)['id']
            self.api.del_msg(event.message.peer_id, msg_id_del)
        self.api.edit_msg(msg_id['peer_id'], msg_id['conversation_message_id'], answer, attachment=photo if photo else None)

    if 'положили' in event.message.text or 'взяли' in event.message.text:
        if event.chat_id == GUILD_CHAT_ID:
            logger.info('Storage\t'+event.message.text.encode('cp1251', 'xmlcharrefreplace').decode('cp1251').replace('\n', ' | '))
            storage_reactions(self, event)
            pass

    if 'от игрока' in event.message.text:
        if event.chat_id == GUILD_CHAT_ID:
            logger.info('Transfer\t'+event.message.text.encode('cp1251', 'xmlcharrefreplace').decode('cp1251').replace('\n', ' | '))
            pass
    return


def profile_message(self: VkBot, event: VkBotEvent) -> str:
    data = parse_profile(event.message.text)
    data_old = user_data.get_user_data(data['id_vk'])
    new_data = (data['id_vk'], data['level'], data['attack'], data['defence'],
                data['strength'], data['agility'], data['endurance'],
                data['luck'], None, None)
    if data_old:
        answer = f"{data['name']}, статы обновлены! ({datediff(data_old['last_update'], datetime.now())} с {str_datetime(data_old['last_update'])})\n" \
                 f"[ {data['class_name']} | {data['race']} ]\n" \
                 f"&#128128;{data['level']}({data['level'] - data_old['level']}) " \
                 f"&#128481;{data['attack']}({data['attack'] - data_old['attack']}) " \
                 f"&#128737;{data['defence']}({data['defence'] - data_old['defence']})\n" \
                 f"&#128074;{data['strength']}({data['strength'] - data_old['strength']}) " \
                 f"&#128400;{data['agility']}({data['agility'] - data_old['agility']}) " \
                 f"&#10084;{data['endurance']}({data['endurance'] - data_old['endurance']})\n" \
                 f"&#127808;{data['luck']}({data['luck'] - data_old['luck']})\n" \
                 f"(До пинка {(data['level'] + 15) * 6 - data['strength'] - data['agility']}&#128074;/&#128400; или " \
                 f"{data['level'] * 3 + 45 - data['endurance']}&#10084;)"
        user_data.update_user_data(*new_data)
    else:
        answer = f"{data['name']}, статы записаны!\n" \
                 f"[ {data['class_name']} | {data['race']} ]\n" \
                 f"&#128128;{data['level']} &#128481;{data['attack']} &#128737;{data['defence']} " \
                 f"&#128074;{data['strength']} &#128400;{data['agility']} &#10084;{data['endurance']} " \
                 f"&#127808;{data['luck']}\n" \
                 f"(До пинка {(data['level'] + 15) * 6 - data['strength'] - data['agility']}&#128074;/&#128400; или " \
                 f"{(data['level'] + 15) * 3 - data['endurance']}&#10084;)"
        user_data.add_user_data(*new_data)

    if data['guild'] == GUILD_NAME:
        if users.get_user(data['id_vk']):
            answer = 'Обновил информацию гильдии!\n' + answer
            users.update_user(data['id_vk'], class_id=data['class_id'])
        else:
            answer = 'Записал информацию гильдии!\n' + answer
            users.add_user(data['id_vk'], None, True, False, False, None, data['class_id'])
    return answer


def storage_reactions(self: VkBot, event: VkBotEvent):

    gold_emoji = '&#127765;'

    data = parse_storage_action(event.message.text)
    if data['item_type'] == 'book':
        cur_balance = users.change_balance(data['id_vk'], data['result_price']*data['count'])
        if data['result_price'] > 0:
            msg = f"О, [id{data['id_vk']}|Вы] взяли {data['count']} штук {data['item_name']}!\n"
        else:
            msg = f"О, [id{data['id_vk']}|Вы] положили {data['count']} штук {data['item_name']}!\n"

        msg += f"Я вижу, они стоят в среднем {gold_emoji}{data['price']}({abs(data['result_price'])}), так что я "
        msg += "пополняю баланс на" if data['result_price'] > 0 else "списываю с баланса"
        msg += f" {abs(data['result_price']*data['count'])}{gold_emoji}\n"

        msg += f"Ваш долг: {gold_emoji}{-cur_balance}(Положить {round(-cur_balance/(100-COMMISSION_PERCENT)/100)})" if cur_balance < 0 else f"Сейчас на счету: {gold_emoji}{cur_balance}"
        self.api.send_chat_msg(event.chat_id, msg)
        return

    if data['item_type'] == 'gold':
        cur_balance = users.change_balance(data['id_vk'], data['count'])
        if data['count'] < 0:
            msg = f"О, [id{data['id_vk']}|Вы] взяли {-data['count']} золота!\n"
        else:
            msg = f"О, [id{data['id_vk']}|Вы] положили {data['count']} золота!\n"
        msg += f"Ваш долг: {gold_emoji}{-cur_balance}(Положить {round(cur_balance/(100-COMMISSION_PERCENT)/100)})" if cur_balance < 0 else f"Сейчас на счету: {gold_emoji}{cur_balance}"
        self.api.send_chat_msg(event.chat_id, msg)
        return

    return
