# builtins
import json

# requirement's import
from vk_api.bot_longpoll import VkBotEvent

# config and packages
from config import GUILD_CHAT_ID

from ORM import session, UserInfo, UserStats, Item, Logs

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

        Logs(event.message.from_id,
             'Profile_link',
             ).make_record()

        ans = 'Пару секунд, мне нужно изучить твои статы и экипировку...'
        msg_id = self.api.send_user_msg(event.message.from_id, ans)[0]

        s = event.message.text[event.message.text.find('act='):event.message.text.find('&group_id')]
        auth = s[s.find('auth_key') + 9:s.find('auth_key') + 41]
        profile = get_profile(auth, event.message.from_id)

        DB = session()

        inv = [int(i) for i in profile['items']]
        class_id = inv[0] if inv[0] != 14108 else inv[1]
        class_name: Item = DB.query(Item).filter(Item.item_id == class_id).first()
        build = get_books(inv)

        stats = profile['stats']
        new_data = (class_id,
                    stats['level'], stats['attack'], stats['defence'],
                    stats['strength'], stats['agility'], stats['endurance'],
                    stats['luck'], stats['accuracy'], stats['concentration'])
        info: UserInfo = DB.query(UserInfo).filter(UserInfo.user_id == event.message.from_id).first()

        if info:
            info.user_profile_key = auth

            info.user_items = [DB.query(Item).filter(Item.item_id == i).first()
                               for i in build]
            stats: UserStats = info.user_stats
            stats.class_id, stats.user_level, stats.user_attack, stats.user_defence, stats.user_strength, \
                stats.user_agility, stats.user_endurance, stats.user_luck, stats.user_accuracy, \
                stats.user_concentration = new_data

            ans = f"Обновил твой профиль! Значит, твой высший класс {class_name.item_name}?\n" \
                  f"Похвально, я буду сообщать о тебе, когда твои книги будут на продаже"
        else:
            info = UserInfo()
            stats = UserStats()

            info.user_id = event.message.from_id
            info.user_profile_key = auth
            info.user_items = [DB.query(Item).filter(Item.item_id == i).first()
                               for i in build]

            stats.user_id = event.message.from_id
            stats.class_id, stats.user_level, stats.user_attack, stats.user_defence, stats.user_strength, \
                stats.user_agility, stats.user_endurance, stats.user_luck, stats.user_accuracy, \
                stats.user_concentration = new_data

            ans = f"В первый раз, значит? Что ж, проходи, сейчас запишу... \n" \
                  f"Так, высший класс {class_name.item_name}, хорошо...\n" \
                  f"Готово, теперь я буду сообщать о тебе, когда твои книги будут на продаже"

        DB.add(info)
        DB.add(stats)
        DB.commit()
        self.api.edit_msg(msg_id['peer_id'], msg_id['conversation_message_id'], ans)
    return
