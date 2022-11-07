# builtins
from datetime import datetime
import logging
import time

# requirement's import
from vk_api.bot_longpoll import VkBotEvent

# config and packages
from config import GUILD_NAME

import DB.users as users
import DB.user_data as user_data

from utils.parsers import parse_profile
from utils.formatters import str_datetime, datediff

# import for typing hints
from vk_bot.vk_bot import VkBot


def bot_message(self: VkBot, event: VkBotEvent):
    # group's message in chat

    txt = event.message.text.encode('cp1251', 'xmlcharrefreplace').decode('cp1251').replace('\n', ' | ')
    logging.info(f"{time.strftime('%d %m %Y %H:%M:%S')}\t\t[{event.chat_id}]\t #OVERSEER: {txt}")
    del txt

    if "Ваш профиль:" in event.message.text:
        msg_id = self.api.send_chat_msg(event.chat_id, 'Читаю профиль...')[0]

        data = parse_profile(event.message.text)
        data_old = user_data.get_user_data(data['id_vk'])
        new_data = (data['id_vk'], data['level'], data['attack'], data['defence'],
                    data['strength'], data['agility'], data['endurance'],
                    data['luck'], None, None)
        if data_old:
            answer = f"Статы обновлены! ({datediff(data_old['last_update'], datetime.now())} с {str_datetime(data_old['last_update'])})\n" \
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
            answer = f"Статы записаны!\n&#128128;{data['level']} &#128481;{data['attack']} &#128737;{data['defence']} " \
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

        self.api.edit_msg(msg_id['peer_id'], msg_id['conversation_message_id'], answer)

    return
