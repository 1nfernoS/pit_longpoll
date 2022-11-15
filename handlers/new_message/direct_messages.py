# builtins
import json

# requirement's import
from vk_api.bot_longpoll import VkBotEvent

# config and packages
from config import GUILD_CHAT_ID

from DB.items import get_item_by_id
import DB.users as users
import DB.user_data as user_data

from profile_api import get_profile, get_books

# import for typing hints
from vk_bot.vk_bot import VkBot


def user_message(self: VkBot, event: VkBotEvent):
    # direct message from user
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
            ans = f"В первый раз, значит? Что ж, проходи, сейчас запишу... \n" \
                  f"Так, высший класс {get_item_by_id(class_id)}, хорошо...\n" \
                  f"Готово, теперь я буду сообщать о тебе, когда твои книги будут на продаже"

        self.api.send_user_msg(event.message.from_id, ans)
    return
