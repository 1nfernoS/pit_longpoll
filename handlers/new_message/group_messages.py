# builtins
from datetime import datetime

# requirement's import
from vk_api.bot_longpoll import VkBotEvent

# config and packages
from config import GUILD_NAME, GUILD_CHAT_ID, COMMISSION_PERCENT

import DB.users as users
import DB.user_data as user_data

from utils.parsers import parse_profile, parse_storage_action
from utils.formatters import str_datetime, datediff
from utils.math import commission_price
import utils.emoji as emo

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
                 f"{emo.level_emoji}{data['level']}({data['level'] - data_old['level']}) " \
                 f"{emo.attack_emoji}{data['attack']}({data['attack'] - data_old['attack']}) " \
                 f"{emo.defence_emoji}{data['defence']}({data['defence'] - data_old['defence']})\n" \
                 f"{emo.strength_emoji}{data['strength']}({data['strength'] - data_old['strength']}) " \
                 f"{emo.agility_emoji}{data['agility']}({data['agility'] - data_old['agility']}) " \
                 f"{emo.endurance_emoji}{data['endurance']}({data['endurance'] - data_old['endurance']})\n" \
                 f"{emo.luck_emoji}{data['luck']}({data['luck'] - data_old['luck']})\n" \
                 f"(До пинка {(data['level'] + 15) * 6 - data['strength'] - data['agility']}{emo.strength_emoji}/{emo.agility_emoji}" \
                 f" или {(data['level'] + 15) * 3 - data['endurance']}{emo.endurance_emoji})"
        user_data.update_user_data(*new_data)
    else:
        answer = f"{data['name']}, статы записаны!\n" \
                 f"[ {data['class_name']} | {data['race']} ]\n" \
                 f"{emo.level_emoji}{data['level']} {emo.attack_emoji}{data['attack']} {emo.defence_emoji}{data['defence']} " \
                 f"{emo.strength_emoji}{data['strength']} {emo.agility_emoji}{data['agility']} {emo.endurance_emoji}{data['endurance']} " \
                 f"{emo.luck_emoji}{data['luck']}\n" \
                 f"(До пинка {(data['level'] + 15) * 6 - data['strength'] - data['agility']}{emo.strength_emoji}/{emo.agility_emoji}" \
                 f"{(data['level'] + 15) * 3 - data['endurance']}{emo.endurance_emoji})"
        user_data.add_user_data(*new_data)

    if data['guild'] == GUILD_NAME:
        if users.get_user(data['id_vk']):
            answer = 'Обновил информацию гильдии!\n' + answer
            users.update_user(data['id_vk'], is_active=1)
        else:
            answer = 'Записал информацию гильдии!\n' + answer
            users.add_user(data['id_vk'], None, True, False, False, None, data['class_id'])
    return answer


def storage_reactions(self: VkBot, event: VkBotEvent):
    data = parse_storage_action(event.message.text)
    if data['item_type'] == 'book':
        cur_balance = users.change_balance(data['id_vk'], data['result_price']*data['count'])

        msg = f"[id{data['id_vk']}|Готово], "
        msg += "пополняю баланс на" if data['result_price'] > 0 else "списываю с баланса"
        msg += f" {abs(data['result_price']*data['count'])}{emo.gold_emoji}({data['count']}*{abs(data['result_price'])})\n"

        msg += f"Ваш долг: {emo.gold_emoji}{-cur_balance}(Положить {commission_price(-cur_balance)})" \
            if cur_balance < 0 else f"Сейчас на счету: {emo.gold_emoji}{cur_balance}"
        self.api.send_chat_msg(event.chat_id, msg)
        return

    if data['item_type'] == 'gold':
        cur_balance = users.change_balance(data['id_vk'], data['count'])
        if data['count'] < 0:
            msg = f"О, [id{data['id_vk']}|Вы] взяли {-data['count']} золота!\n"
        else:
            msg = f"О, [id{data['id_vk']}|Вы] положили {data['count']} золота!\n"
        msg += f"Ваш долг: {emo.gold_emoji}{-cur_balance}(Положить {commission_price(-cur_balance)})" \
            if cur_balance < 0 else f"Сейчас на счету: {emo.gold_emoji}{cur_balance}"
        self.api.send_chat_msg(event.chat_id, msg)
        return

    return
