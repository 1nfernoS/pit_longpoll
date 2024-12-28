from typing import List, TYPE_CHECKING

from commands import Command

from ORM import session, UserInfo, Item, Logs

from config import GUILD_NAME, DISCOUNT_PERCENT

import profile_api

import utils.math
from dictionaries.emoji import gold, item, tab, active_book, passive_book

if TYPE_CHECKING:
    from vk_api.bot_longpoll import VkBotEvent
    from vk_bot.vk_bot import VkBot


class Price(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('цена',))
        self.desc = 'Узнать цену предмета на аукционе и внутри гильдии. Можно указать число перед поиском'
        self.require_balance = True
        # self.set_active(False)
        return

    def run(self, bot: "VkBot", event: "VkBotEvent"):

        s = session()
        user: UserInfo = s.query(UserInfo).filter(UserInfo.user_id == event.message.from_id).first()
        if not user.user_role.role_can_balance:
            return

        Logs(event.message.from_id, __class__.__name__, reason=event.message.text).make_record()

        msg_id = bot.api.send_chat_msg(event.chat_id, 'Ищу ценники . . .')[0]
        msg = event.message.text.split(' ')
        if len(msg) == 1:
            bot.api.edit_msg(msg_id['peer_id'], msg_id['conversation_message_id'], 'А что искать...')
            return

        try:
            count = int(msg[1])
            item_name = ' '.join(msg[2:])
        except ValueError:
            if not all([i.isalpha() for i in msg[1]]):
                del_id = bot.api.get_conversation_msg(msg_id['peer_id'], msg_id['conversation_message_id'])['id']
                bot.api.del_msg(msg_id['peer_id'], del_id)
                return
            count = 1
            item_name = ' '.join(msg[1:])

        if len(item_name) < 3:
            bot.api.edit_msg(msg_id['peer_id'], msg_id['conversation_message_id'],
                             'Добавьте пару букв к поиску, чтобы их было хотя бы 3')
            return

        search: List[Item] = s.query(Item).filter(
            Item.item_name.op('regexp')(f"(Книга - |Книга - [[:alnum:]]+ |^[[:alnum:]]+ |^){item_name}.*$"),
            Item.item_has_price == 1).all()

        if not search:
            bot.api.edit_msg(msg_id['peer_id'], msg_id['conversation_message_id'], 'Ничего не нашлось...')
            return

        answer = ''
        cnt = 0
        for i in search:
            auc_price = profile_api.price(i.item_id)
            if auc_price <= 0:
                continue

            guild_price = utils.math.discount_price(auc_price)
            guild_commission_price = utils.math.commission_price(guild_price)
            answer += f"\n{gold}{auc_price*count} " if count > 1 else f"\n{gold}{auc_price} "
            answer += f"[-{DISCOUNT_PERCENT}%:{gold}{guild_price*count}" \
                if count > 1 \
                else f"[-{DISCOUNT_PERCENT}%:{gold}{guild_price}"
            answer += f"({gold}{guild_commission_price*count})] " if count > 1 else f"({gold}{guild_commission_price})]"
            answer += f" {item}{count}*{i.item_name}" if count > 1 else f"{item}{i.item_name}"
            cnt += 1

        answer = f"Нашел следующее:" + answer if cnt > 0 else 'Ничего не нашлось...'

        bot.api.edit_msg(msg_id['peer_id'], msg_id['conversation_message_id'], answer)
        s.close()
        return


class Equip(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('экип', 'билд', 'equip', 'build'))
        self.desc = 'Показать свою экипировку. Доступно членам гильдии, которые сдавали ссылку на профиль в лс бота'
        self.require_profile_app_check = True
        # self.set_active(False)
        return

    @staticmethod
    def __get_list(item_list: list, skills: dict) -> str:
        message = ''
        s = session()

        for book in item_list:
            b_item: Item = s.query(Item).filter(Item.item_id == book).first()

            lvl = None
            if "(А) " in b_item.item_name:
                book_name = b_item.item_name.replace("(А) ", f"{tab}{active_book}")
                lvl = [v for k, v in skills['active'].items() if b_item.item_name[4:].startswith(k[:-1])]
                
            if "(П) " in b_item.item_name:
                book_name = b_item.item_name.replace("(П) ", f"{tab}{passive_book}")
                lvl = [v for k, v in skills['passive'].items() if b_item.item_name[4:].startswith(k[:-1])]
            message += '\n' + f'{book_name}'
            if lvl:
                message += f" - {lvl[0]} ({(round((int(lvl[0]) / 10) ** 0.5 * 10) + 100)}%)"
        s.close()
        return message

    def run(self, bot: "VkBot", event: "VkBotEvent"):
        s = session()

        user: UserInfo = s.query(UserInfo).filter(UserInfo.user_id == event.message.from_id).first()

        if not user:
            msg = f"Не могу найти записей, покажите свой профиль, чтобы я записал информацию о вас и вашей гильдии"
            bot.api.send_chat_msg(event.chat_id, msg)
            return

        if user.user_role.role_can_moderate:
            if 'reply_message' in event.message.keys():
                reply_to = event.message.reply_message['from_id']
                user: UserInfo = s.query(UserInfo).filter(UserInfo.user_id == reply_to).first()

        if not user.user_role.role_can_profile_app_check:
            bot.api.send_chat_msg(event.chat_id, f"Нет, это только для членов гильдии {GUILD_NAME}!")
            return

        if not user.user_profile_key:
            message = "Сдайте ссылку на профиль мне в лс!\n" \
                      "Проще всего это сделать через сайт, скопировав адрес ссылки кнопки 'Профиль' в приложении.\n" \
                      "Если получилась ссылка формата 'https:// vip3.activeusers .ru/блаблабла', то все получится)"
            bot.api.send_chat_msg(event.chat_id, message)
            return

        msg_id = bot.api.send_chat_msg(event.chat_id, 'Поднимаю записи . . .')[0]

        profile = profile_api.get_profile(user.user_profile_key, user.user_id)

        inv = [int(i) for i in profile['items']]

        build = profile_api.get_books(inv)

        user.user_items = [s.query(Item).filter(Item.item_id == i).first()
                           for i in build]
        build = profile_api.get_build(inv)

        skills = profile_api.lvl_skills(user.user_profile_key, user.user_id)

        message = f'Билд {bot.api.get_names([user.user_id])}:'
        if build['books']:
            message += '\nКниги:'
            message += self.__get_list(build['books'], skills)

        if build['adms']:
            message += '\nВ адмах:'
            message += self.__get_list(build['adms'], skills)
            
        if build['weapons']:
            message += '\nВ оружии:'
            message += self.__get_list(build['weapons'], skills)
            
        bot.api.edit_msg(msg_id['peer_id'], msg_id['conversation_message_id'], message)

        s.add(user)
        s.commit()
        s.close()
        return
