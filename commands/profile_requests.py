from commands import Command

import json

from config import GUILD_CHAT_ID, GUILD_NAME, DISCOUNT_PERCENT, COMMISSION_PERCENT

from DB import items, users

import profile_api

import utils.math
from utils.emoji import gold, item, tab, active_book, passive_book

# import for typing hints
from vk_api.bot_longpoll import VkBotEvent
from vk_bot.vk_bot import VkBot


class Price(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('цена',))
        self.desc = 'Узнать цену предмета на аукционе и внутри гильдии'
        # self.set_active(False)
        return

    def run(self, bot: VkBot, event: VkBotEvent):

        msg_id = bot.api.send_chat_msg(event.chat_id, 'Ищу ценники . . .')[0]
        msg = event.message.text.split(' ')
        if len(msg) == 1:
            bot.api.edit_msg(msg_id['peer_id'], msg_id['conversation_message_id'], 'А что искать...')
            return

        try:
            count = int(msg[1])
            item_name = ' '.join(msg[2:])
        except ValueError:
            count = 1
            item_name = ' '.join(msg[1:])

        if len(item_name) < 3:
            bot.api.edit_msg(msg_id['peer_id'], msg_id['conversation_message_id'],
                             'Добавьте пару букв к поиску, чтобы их было хотя бы 3')
            return

        search = items.search_item(item_name)
        if not search:
            bot.api.edit_msg(msg_id['peer_id'], msg_id['conversation_message_id'], 'Ничего не нашлось...')
            return

        answer = ''
        cnt = 0
        for i in search['result']:
            auc_price = profile_api.price(i['item_id'])
            if auc_price <= 0:
                continue

            guild_price = utils.math.discount_price(auc_price)
            guild_commission_price = utils.math.commission_price(guild_price)
            answer += f"\n{gold}{auc_price*count} " if count > 1 else f"\n{gold}{auc_price} "
            answer += f"[-{DISCOUNT_PERCENT}%:{gold}{guild_price*count}" if count > 1 else f"[-{DISCOUNT_PERCENT}%:{gold}{guild_price}"
            answer += f"({gold}{guild_commission_price*count})] " if count > 1 else f"({gold}{guild_commission_price})] "
            answer += f"{item}{count}*{i['item_name']}" if count > 1 else f"{item}{i['item_name']}"
            cnt += 1

        answer = f"Нашел следующее ({cnt}):" + answer if cnt > 0 else 'Ничего не нашлось...'

        bot.api.edit_msg(msg_id['peer_id'], msg_id['conversation_message_id'], answer)

        return


class Equip(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('экип', 'билд', 'equip', 'build'))
        self.desc = 'Показать свою экипировку. Доступно членам гильдии, которые сдавали ссылку на профиль в лс бота'
        self.set_access('guild')
        # self.set_active(False)
        return

    @staticmethod
    def __get_list(item_list: list, skills: dict) -> str:
        message = ''
        for book in item_list:
            name = items.get_item_by_id(book)

            message += '\n' + f'{name.replace("(А) ", f"{tab}{active_book}").replace("(П) ", f"{tab}{passive_book}")}'
            lvl = [v for k,v in skills.items() if name[4:].startswith(k)]
            if lvl:
                message += f" - {lvl[0][0]} ({int(lvl[0][1] * 100)}%)"
        return message

    def run(self, bot: VkBot, event: VkBotEvent):

        if event.message.from_id not in bot.api.get_members(GUILD_CHAT_ID):
            bot.api.send_chat_msg(event.chat_id, f"Нет, это только для членов гильдии {GUILD_NAME}!")
            return

        data = users.get_user(event.message.from_id)
        if not data:
            bot.api.send_chat_msg(event.chat_id, f"Не могу найти записей, покажите сой профиль, чтобы я записал информацию о вас и вашей гильдии")
            return

        if not data['profile_key']:
            message = "Сдайте ссылку на профиль мне в лс!\n" \
                      "Проще всего это сделать через сайт, скопировав адрес ссылки кнопки 'Профиль' в приложении.\n" \
                      "Если получилась ссылка формата 'https:// vip3.activeusers .ru/блаблабла', то все получится)"
            bot.api.send_chat_msg(event.chat_id, message)
            return

        msg_id = bot.api.send_chat_msg(event.chat_id, 'Поднимаю записи . . .')[0]

        profile = profile_api.get_profile(data['profile_key'], event.message.from_id)

        inv = [int(i) for i in profile['items']]

        class_id = inv[0] if inv[0] != 14108 else inv[1]
        build = profile_api.get_books(inv)
        users.update_user(event.message.from_id, is_active=1, equipment=json.dumps(build),
                          class_id=class_id)

        build = profile_api.get_build(inv)

        skills = profile_api.lvl_active(data['profile_key'], event.message.from_id)
        skills.update(profile_api.lvl_passive(data['profile_key'], event.message.from_id))

        message = f'Билд {bot.api.get_names([event.message.from_id])}:'
        if build['books']:
            message += '\nКниги:'
            message += self.__get_list(build['books'], skills)

        if build['adms']:
            message += '\nВ адмах:'
            message += self.__get_list(build['adms'], skills)

        bot.api.edit_msg(msg_id['peer_id'], msg_id['conversation_message_id'], message)
        return
