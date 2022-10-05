from commands import Command

import json

from config import GUILD_CHAT_ID, GUILD_NAME

from DB import items, users, user_data

import profile_api

# import for typing hints
from vk_api.bot_longpoll import VkBotEvent
from vk_bot.vk_bot import VkBot


class Price(Command):

    desc = 'Узнать цену предмета на аукционе и внутри гильдии'

    def __init__(self):
        super().__init__(__class__.__name__, ('цена',))
        # self.set_active(False)
        return

    def run(self, bot: VkBot, event: VkBotEvent, text: str = None):
        item_name = event.message.text.split(' ', 1)[1]

        search = items.search_item(item_name)
        if search:
            item_emoji = '&#128093;'
            gold_emoji = '&#127765;'

            answer = ''
            cnt = 0
            for i in search['result']:
                auc_price = profile_api.price(i['item_id'])
                if auc_price > 0:
                    answer += f"\n{gold_emoji}{auc_price} ({gold_emoji}{round(auc_price/0.9)}) {item_emoji}{i['item_name']}"
                    cnt += 1
            if cnt > 0:
                answer = f"Нашел следующее ({cnt}):" + answer
            else:
                answer = 'Ничего не нашлось...'
        else:
            answer = 'Ничего не нашлось...'

        bot.api.send_chat_msg(event.chat_id, answer)

        return


class Equip(Command):

    desc = 'Показать свою экипировку. Достпно членам гильдии, которые сдавали ссылку на профиль в лс бота'

    def __init__(self):
        super().__init__(__class__.__name__, ('экип', 'билд', 'equip', 'build'))
        # self.set_active(False)
        return

    def run(self, bot: VkBot, event: VkBotEvent):

        if event.message.from_id not in bot.api.get_members(GUILD_CHAT_ID):
            message = f'Нет, это только для членов гильдии {GUILD_NAME}!'

        data = users.get_user(event.message.from_id)

        if data['profile_key']:

            profile = profile_api.get_profile(data['profile_key'], event.message.from_id)
            stats = profile['stats']

            new_data = (event.message.from_id,
                        stats['level'], stats['attack'], stats['defence'],
                        stats['strength'], stats['agility'], stats['endurance'],
                        stats['luck'], stats['accuracy'], stats['concentration'])
            user_data.update_user_data(*new_data)

            inv = [int(i) for i in profile['items']]

            class_id = inv[0] if inv[0] != 14108 else inv[1]
            build = profile_api.get_books(inv)
            users.update_user(event.message.from_id, is_active=1, equipment=json.dumps(build),
                              class_id=class_id)

            build = profile_api.get_build(inv)
            message = f'Билд {bot.api.get_names([event.message.from_id])}:'
            if build['books']:
                message += '\nКниги:'
                for item in build['books']:
                    message += '\n'+f'{items.get_item_by_id(item)}'
            if build['adms']:
                message += '\nВ адмах:'
                for item in build['adms']:
                    message += '\n' + f'{items.get_item_by_id(item)}'

        else:
            message = "Сдайте ссылку на профиль мне в лс!\n" \
                      "Проще всего это сделать через сайт, скопировав адрес ссылки кнопки 'Профиль' в приложении.\n" \
                      "Если получилась ссылка формата 'https:// vip3.activeusers .ru/блаблабла', то все получится)"

        bot.api.send_chat_msg(event.chat_id, message)
        return

