import json
from datetime import datetime

from vk_api.bot_longpoll import CHAT_START_ID, VkBotEvent

from config import OVERSEER_BOT, PIT_BOT, GUILD_NAME, GUILD_CHAT_ID

# import for typing hints
from vk_bot.vk_bot import VkBot

from profile_api import get_profile, get_books

from DB.items import get_item_by_name, get_item_by_id
import DB.users as users
import DB.user_data as user_data

from .forwards import forward_parse


def new_message(self: VkBot, event: VkBotEvent):
    if event.from_user:
        if len(event.message.attachments) != 0:
            at = event.message.attachments[0]
            if at['type'] == 'link':
                if event.message.text == "":
                    event.message.text = at['link']['url']

        if 'https://vip3.activeusers.ru/app.php?' in event.message.text:
            if event.message.from_id not in self.api.get_members(GUILD_CHAT_ID):
                ans = "Я надеюсь, ты понимаешь, что только что предоставил ПОЛНЫЙ доступ к своему профилю?\n" \
                      "Ладно уж, я в него не полезу, но лучше так больше не делай"
                self.api.send_user_msg(event.message.from_id, ans)
                return

            ans = 'Пару секунд, мне нужно изучить твои статы и экипировку... Один раз'
            self.api.send_user_msg(event.message.from_id, ans)

        s = event.message.text[event.message.text.find('act='):event.message.text.find('&group_id')]
        auth = s[s.find('auth_key') + 9:s.find('auth_key') + 41]
        profile = get_profile(auth, event.message.from_id)

        stats = profile['stats']
        new_data = (event.message.from_id,
                    stats['level'], stats['attack'], stats['defence'],
                    stats['strength'], stats['agility'], stats['endurance'],
                    stats['luck'], stats['accuracy'], stats['concentration'])

        user_data.update_user_data(*new_data)

        inv = [int(i) for i in profile['items']]
        class_id = inv[0] if inv[0] != 14108 else inv[1]
        build = get_books(inv)
        data_old = users.get_user(event.message.from_id)
        if data_old:
            users.update_user(event.message.from_id, profile_key=auth, is_active=1, equipment=json.dumps(build),
                              class_id=class_id)
            ans = f"Обновил твой профиль! Значит, твой высший класс {get_item_by_id(class_id)}?\n" \
                  f"Похвально, я буду сообщать о тебе, когда твои книги будут на продаже"
        else:
            users.add_user(event.message.from_id, auth, True, False, False, json.dumps(build), class_id)
            ans = f"В первый раз, значит? Чтож, проходи, сейчас запишу... \n" \
                  f"Так, высший класс {get_item_by_id(class_id)}, хорошо...\n" \
                  f"Готово, теперь я буду сообщать о тебе, когда твои книги будут на продаже"

        self.api.send_user_msg(event.message.from_id, ans)
        return

    if event.from_chat:
        if event.message.from_id == OVERSEER_BOT:
            if "Ваш профиль:" in event.message.text:
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
                             f"{data['level'] * 3 + 45 - data['endurance']}&#10084;)"
                    user_data.add_user_data(*new_data)

                if data['guild'] == GUILD_NAME:
                    if users.get_user(data['id_vk']):
                        answer = 'Обновил информацию гильдии!\n' + answer
                        users.update_user(data['id_vk'], is_officer=data['is_officer'], class_id=data['class_id'])
                    else:
                        answer = 'Записал информацию гильдии!\n' + answer
                        users.add_user(data['id_vk'], None, True, False, data['is_officer'], None, data['class_id'])

                self.api.send_chat_msg(event.chat_id, answer)

    if len(event.message.fwd_messages) == 1:
        if int(event.message.fwd_messages[0]['from_id']) == int(PIT_BOT):
            forward_parse(self, event)
            pass
        return

    return


def parse_profile(text: str) -> dict:
    text = text.encode('cp1251', 'xmlcharrefreplace').decode('cp1251')
    import re
    officer_emoji = '&#11088;'
    t = text.split('\n')

    id_vk = int(re.findall(r'(?<=id)\d+', t[0])[0])

    class_name = t[1][16:t[1].find(',')]
    class_id = get_item_by_name(class_name)

    guild = t[2][18:]
    is_officer = guild.endswith(officer_emoji)
    guild = guild[:-len(officer_emoji)] if is_officer else guild

    level = int(re.findall(r' \d+', t[4])[0])

    strength = int(re.findall(r'(?<=&#128074;)\d+', t[7])[0])
    agility = int(re.findall(r'(?<=&#128400;)\d+', t[7])[0])
    endurance = int(re.findall(r'(?<=&#10084;)\d+', t[7])[0])
    luck = int(re.findall(r'(?<=&#127808;)\d+', t[7])[0])
    attack = int(re.findall(r'(?<=&#128481;)\d+', t[7])[0])
    defence = int(re.findall(r'(?<=&#128737;)\d+', t[7])[0])

    res = {'id_vk': id_vk, 'guild': guild, 'is_officer': is_officer, 'class_id': class_id, 'level': level,
           'strength': strength, 'agility': agility, 'endurance': endurance, 'luck': luck, 'attack': attack,
           'defence': defence, 'last_update': datetime.now()}
    return res


def str_datetime(d: datetime) -> str:
    return '{:0>2}'.format(d.day) + '.' + '{:0>2}'.format(d.month) + '.' + '{:0>2}'.format(d.year % 100) + ' ' + \
           '{:0>2}'.format(d.hour) + ':' + '{:0>2}'.format(d.minute)


def datediff(d1: datetime, d2: datetime) -> str:
    diff = max(d1, d2) - min(d1, d2)
    res = 'Прошло '
    if diff.days:
        res += str(diff.days)
        if diff.days // 10 == 1 or diff.days % 10 > 4:
            res += ' дней '
        elif diff.days % 10 > 1:
            res += ' дня '
        elif diff.days % 10 == 1:
            res += ' день '
    h = diff.seconds // 3600
    if h:
        res += str(h)
        if h // 10 == 1 or h % 10 > 4 or h % 10 == 0:
            res += ' часов '
        elif h % 10 > 1:
            res += ' часа '
        elif h % 10 == 1:
            res += ' час '
    m = diff.seconds % 3600 // 60
    if m:
        res += str(m)
        if m // 10 == 1 or m % 10 > 4 or m % 10 == 0:
            res += ' минут '
        elif m % 10 > 1:
            res += ' минуты '
        elif m % 10 == 1:
            res += ' минута '
    return res.strip()
