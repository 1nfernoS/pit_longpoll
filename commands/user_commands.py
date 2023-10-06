from typing import List, TYPE_CHECKING

import vk_api
from vk_api.exceptions import ApiError
from vk_api.bot_longpoll import CHAT_START_ID

import profile_api
from commands import Command, command_list

from ORM import session, UserInfo, UserStats, Item, Logs, Role

from config import creator_id, GUILD_CHAT_ID, GUILD_NAME, storager_token, storager_chat

from dictionaries import roles
from dictionaries.emoji import level, strength, agility, endurance, gold, item
import dictionaries.items as items
from utils.math import commission_price, discount_price
from utils.keyboards import notes

if TYPE_CHECKING:
    from vk_api.bot_longpoll import VkBotEvent
    from vk_bot.vk_bot import VkBot


class Stats(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('stats', 'пинок', 'статы'))
        self.desc = 'Узнать сколько статов осталось до принудительного перехода на следующий этаж'
        self.require_check_stats = True
        # self.set_active(False)
        return

    def run(self, bot: "VkBot", event: "VkBotEvent"):
        s = session()

        user: UserStats = s.query(UserStats).filter(UserStats.user_id == event.message.from_id).first()

        if user.user_info.user_role.role_can_moderate:
            if 'reply_message' in event.message.keys():
                user: UserInfo = s.query(UserStats).filter(
                    UserStats.user_id == event.message.reply_message['from_id']).first()

        if not user.user_info.user_role.role_can_check_stats:
            return

        Logs(event.message.from_id, __class__.__name__, None, None,
             event.message.reply_message['from_id']
             if 'reply_message' in event.message.keys()
             else event.message.from_id).make_record()

        message = f"{user.user_level}{level}: до пинка " \
                  f"{(user.user_level + 15) * 6 - user.user_strength - user.user_agility}{strength}/{agility}" \
                  f" или {user.user_level * 3 + 45 - user.user_endurance}{endurance}" \
            if user \
            else "До пинка... Хм... О вас нет записей, покажите профиль хотя бы раз!!"

        bot.api.send_chat_msg(event.chat_id, message)
        return


class Help(Command):

    def __init__(self):
        super().__init__(__class__.__name__, ('помощь', 'команды', 'help'))
        self.desc = 'Список команд'
        self.require_basic = True
        # self.set_active(False)
        return

    def run(self, bot: "VkBot", event: "VkBotEvent"):
        message = 'Команды можно вводить как с префиксом, так и без\nВарианты использования - что делает\n'

        s = session()
        user: UserInfo = s.query(UserInfo).filter(UserInfo.user_id == event.message.from_id).first()
        role_access = {i.replace('role_can_', ''): bool(getattr(user.user_role, i))
                       for i in dir(user.user_role)
                       if i.startswith('role_can_')}

        Logs(event.message.from_id, __class__.__name__).make_record()

        # data = users.get_user(event.message.from_id)
        for cmd in command_list:
            requires = {i.replace('require_', ''): getattr(command_list[cmd], i)
                        for i in dir(command_list[cmd])
                        if i.startswith('require_') and getattr(command_list[cmd], i)}
            if all([role_access[r] for r in requires]):
                message += '[' + ', '.join(cmd) + '] - ' + command_list[cmd].get_description() + '\n'

        forwards_help = "\nТакже доступны следующие функции для пересылов сообщений от колодца "
        forwards_help += "(хотя бы 1е сообщение в списке должно быть от колодца):\n"
        forwards_help += " - Любой пересыл с таймером - напомнить об окончании таймера (пуш+ответ на сообщение спустя время)\n"
        forwards_help += " - Мрачный торговец (предмет и цена) - проверит ценник с аукционом и подскажет цену с учетом скидки гильдии!\n"
        forwards_help += " - Символы - Подскажет слово в пещере чудес, или хотя бы букву (чтобы не ленились гадать самостоятельно)\n"
        forwards_help += " - Путешествие за городом - Подскажет насколько прокачался навык (без учета удвоения) и подскажет какой этап путешествия сейчас\n"
        forwards_help += " - Загадки двери - подскажет ответ на загадку\n"
        forwards_help += " - Страницы книги - подскажет книгу по описанию тлеющей страницы\n"
        forwards_help += " - Перекресток с указателями - подскажет событие по каждому из путей\n"
        forwards_help += " - Сдача элитных трофеев - Запишет сдачу для отчета, подскажет сколько трофеев еще требуется досдать\n"
        forwards_help += " - Присоединиться к осаде - запишет ваше участие в осаде\n"
        forwards_help += " - Рыбалка - подсчитает количество лута за рыбалку (первое сообщение должно быть с наживкой, последнее с окончанием рыбалки)\n"

        message += f'\n За идеями/ошибками/вопросами обращаться [id{creator_id}|сюда], ' \
                   f'желательно с приставкой "по котику" или что-то в этом роде'

        try:
            bot.api.send_user_msg(event.message.from_id, message)
            bot.api.send_chat_msg(event.chat_id, "Отправил список доступных команд в лс!\n"+forwards_help)
        except ApiError:
            bot.api.send_chat_msg(event.chat_id, "Разреши сообщения, чтобы я мог отправить список команд и попробуй снова\n"
                                  +forwards_help)

        return


class Notes(Command):

    def __init__(self):
        super().__init__(__class__.__name__, ('заметки', 'notes', 'note', 'правила'))
        self.desc = 'Правила и остальные статьи.'
        self.require_basic = True
        # self.set_active(False)
        return

    def run(self, bot: "VkBot", event: "VkBotEvent"):
        s = session()
        user: UserInfo = s.query(UserInfo).filter(UserInfo.user_id == event.message.from_id).first()

        if not user.user_role.role_can_basic:
            return

        Logs(event.message.from_id, __class__.__name__).make_record()

        message = 'Заметки:'
        bot.api.send_chat_msg(event.chat_id, message, notes())
        return


class Balance(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('баланс', 'деньги', 'balance', 'wallet', 'money'))
        self.desc = 'Узнать свой баланс. Только для членов гильдии'
        self.require_balance = True
        # self.set_active(False)
        return

    def run(self, bot: "VkBot", event: "VkBotEvent"):
        s = session()
        user: UserInfo = s.query(UserInfo).filter(UserInfo.user_id == event.message.from_id).first()

        if user is None:
            bot.api.send_chat_msg(event.chat_id, "Хм... О вас нет записей, покажите профиль хотя бы раз!!")
            return

        if not user.user_role.role_can_balance:
            return

        Logs(event.message.from_id,
             __class__.__name__,
             event.message.text,
             None,
             event.message.reply_message['from_id']
             if 'reply_message' in event.message.keys()
             else event.message.from_id
             ).make_record()

        if user.user_role.role_can_check_all_balance:

            if 'reply_message' in event.message.keys():
                reply_user: UserInfo = s.query(UserInfo).filter(
                    UserInfo.user_id == event.message.reply_message['from_id']).first()

                message = f"Счет игрока: {reply_user.balance}" if reply_user is not None \
                    else "Нет записей, пусть сдаст профиль"
                bot.api.send_chat_msg(event.chat_id, message)
                return

            elif len(event.message.text.split(' ')) == 2:
                if event.message.text.split(' ')[1] == 'все':

                    msg_id = bot.api.send_chat_msg(event.chat_id, 'Собираю информацию')[0]

                    guild_roles = (roles.creator, roles.leader, roles.paymaster, roles.librarian,
                                   roles.officer, roles.guild_member, roles.officer_plus, roles.guild_newbie)
                    users: List[UserInfo] = s.query(UserInfo).filter(UserInfo.role_id.in_(guild_roles)).all()

                    members = bot.api.get_members(GUILD_CHAT_ID)
                    message = f'Баланс игроков гильдии {GUILD_NAME}:\n'

                    message += '\n'.join(f"@id{user.user_id}: {user.balance}{gold}"
                                         for user in users
                                         if user.user_id in members)

                    bot.api.send_user_msg(event.message.from_id, message)
                    bot.api.edit_msg(msg_id['peer_id'], msg_id['conversation_message_id'], 'Отправил список в лс')
                    return

        message = f"Ваш долг: {gold}{-user.balance}(Положить {commission_price(-int(user.balance))})" \
            if user.balance < 0 \
            else f"Сейчас на счету: {gold}{user.balance}"
        bot.api.send_chat_msg(event.chat_id, message)
        return


class Who(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('кто',))
        self.desc = '... ест [предмет](Без склонений). Среди тех, кто сдавал профиль или билд'
        self.require_basic = True
        # self.set_active(False)
        return

    def run(self, bot: "VkBot", event: "VkBotEvent"):
        s = session()
        user: UserInfo = s.query(UserInfo).filter(UserInfo.user_id == event.message.from_id).first()

        if user is None:
            bot.api.send_chat_msg(event.chat_id, "Хм... О вас нет записей, покажите профиль хотя бы раз!!")
            return

        if not user.user_role.role_can_basic:
            return

        # msg_id = bot.api.send_chat_msg(event.chat_id, 'Ищу ценники . . .')[0]
        msg = event.message.text.split(' ')
        if len(msg) < 3:
            return
        if msg[1] != 'ест':
            return

        Logs(event.message.from_id, __class__.__name__, event.message.text).make_record()

        item_name = ' '.join(msg[2:])
        search: Item = s.query(Item).filter(
            Item.item_name.op('regexp')(f"(Книга - |Книга - [[:alnum:]]+ ){item_name}.*$"),
            Item.item_has_price == 1).first()

        if not search:
            bot.api.send_chat_msg(event.chat_id, 'Ничего не нашлось...')
            return
        guild_roles = (0, 1, 2, 3, 4, 5, 6)
        message = f'{item}{search.item_name}. В экипировке у ' \
                  f'{bot.api.get_names([i.user_id for i in search.item_users if i.user_role.role_id in guild_roles])}' \
            if search.item_users else f'{item}{search.item_name}. Но этой книги ни у кого в билде нет'

        bot.api.send_chat_msg(event.chat_id, message)

        return


class Transfer(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('перевести', 'transfer'))
        self.desc = 'Перевести деньги со своего счета по реплаю'
        self.require_balance = True
        # self.set_active(False)
        return

    def run(self, bot: "VkBot", event: "VkBotEvent"):
        s = session()
        user_from: UserInfo = s.query(UserInfo).filter(UserInfo.user_id == event.message.from_id).first()

        if user_from is None:
            bot.api.send_chat_msg(event.chat_id, "Хм... О вас нет записей, покажите профиль хотя бы раз!!")
            return

        if not user_from.user_role.role_can_balance:
            return

        if 'reply_message' not in event.message.keys():
            return

        # 2 or 3 word in message (command, value, optional word)
        if 2 > len(event.message.text.split(' ')) > 3:
            return

        try:
            money = int(event.message.text.split(' ')[1])
        except ValueError:
            message = f"Ой, {event.message.text.split(' ')[1]} не число"
            bot.api.send_chat_msg(event.chat_id, message)
            return

        if money < 0:
            message = f"Нет, так не работает"
            bot.api.send_chat_msg(event.chat_id, message)
            return

        if user_from.balance < money:
            message = f"У вас на счету {gold}{user_from.balance}, сначала пополните баланс!"
            bot.api.send_chat_msg(event.chat_id, message)
            return

        user_to: UserInfo = s.query(UserInfo).filter(UserInfo.user_id == event.message.reply_message['from_id']).first()

        if not user_to:
            message = f"О id{user_to.user_id} нет записей, пусть покажет профиль хотя бы раз!"
            bot.api.send_chat_msg(event.chat_id, message)
            return

        if not user_to.user_role.role_can_balance:
            message = f"У id{user_to.user_id} нет прав баланса, проверьте роль или получателя!"
            bot.api.send_chat_msg(event.chat_id, message)
            return

        Logs(event.message.from_id,
             __class__.__name__,
             event.message.text,
             None,
             event.message.reply_message['from_id']
             ).make_record()

        user_from.balance -= money
        user_to.balance += money

        s.add(user_from)
        s.add(user_to)
        s.commit()

        message = f"Перевел {gold}{money}\n"
        message += "Ваш долг: {gold}{-balance}(Положить {commission_price(-balance)})" if user_from.balance < 0 \
            else f"Сейчас на счету: {gold}{user_from.balance}"

        bot.api.send_chat_msg(event.chat_id, message)
        return


class Want(Command):

    def __init__(self):
        super().__init__(__class__.__name__, ('хочу',))
        self.desc = 'Получить со склада желаемый предмет'
        self.require_basic = True
        # self.set_active(False)
        return

    def run(self, bot: "VkBot", event: "VkBotEvent"):
        s = session()
        user: UserInfo = s.query(UserInfo).filter(UserInfo.user_id == event.message.from_id).first()

        if not user.user_role.role_can_basic:
            return

        Logs(event.message.from_id, __class__.__name__, reason=event.message.text).make_record()

        msg = event.message.text.split(' ')
        if len(msg) == 1:
            return

        try:
            count = int(msg[1])
            item_name = ' '.join(msg[2:])
        except ValueError:
            if not all([i.isalpha() for i in msg[1]]):
                return
            count = 1
            item_name = ' '.join(msg[1:])

        if len(item_name) < 3:
            return

        search: Item = s.query(Item).filter(
            Item.item_name.op('regexp')(f"(Книга - |Книга - [[:alnum:]]+ |^[[:alnum:]]+ |^){item_name[:-2]}.*$"),
            Item.item_has_price == 1).first()

        whitelist = {'gold': [items.gold],
                     'books': items.ordinary_books_active + items.ordinary_books_passive,
                     'items': items.base_equipment + items.ingredients_drops + items.ingredients_special +
                              items.materials_raw + items.materials_processed + items.maps}

        if not search:
            bot.api.send_chat_msg(event.chat_id, f'Что-то не могу найти {item_name}')
            return

        role: Role = user.user_role

        # TODO: move balance changes to group message

        if search.item_id in whitelist['gold']:
            if not role.role_can_take_money:
                return

            if count < 100:
                bot.api.send_chat_msg(event.chat_id, f'Нельзя выдать меньше 100{gold}')
                return

            if user.balance < count:
                bot.api.send_chat_msg(event.chat_id, f'Недостаточно средств на балансе')
                return

            message = f'Выдать {count} золота'
            user.balance -= count
            answer = f"Осталось на счету: {gold}{user.balance}"

        elif search.item_id in whitelist['books']:
            if not role.role_can_take_books:
                return

            if count > 10:
                bot.api.send_chat_msg(event.chat_id, f'Многовато книг за раз, больше 10 не дам!')
                return

            book_price = profile_api.price(search.item_id)
            price = discount_price(count * book_price)

            if user.balance < price:
                message = f'Недостаточно средств, это стоит {price}, ' \
                          f'не хватает {gold}{price - user.balance}' \
                          f'(Положить {commission_price(price - user.balance)})'
                bot.api.send_chat_msg(event.chat_id, message)
                return

            message = f'Выдать {search.item_name.replace("Книга - ", "")} - {count} штук'
            user.balance -= price

            answer = f"Выдал {search.item_name.replace('Книга - ', '')}, списываю с баланса{gold}{price}"
            answer += f"({count}*{gold}{discount_price(book_price)})" if count > 1 else ""
            answer += f"\n[id{user.user_id}|Сейчас на счету]: {gold}{user.balance}"
            answer += f"\n(Если книга не выдалась, тегайте лидеров или напишите им в лс)"

        elif search.item_id in whitelist['items']:
            if not role.role_can_take_ingredients:
                return

            message = f'Выдать {search.item_name} - {count} штук'
            answer = ''
        else:
            return

        storager = vk_api.VkApi(token=storager_token, api_version='5.131')
        storager_api = storager.get_api()

        storager_api.messages.send(
            peer_ids=CHAT_START_ID + storager_chat,
            message=message,
            random_id=0,
            disable_mentions=True,
            reply_to=storager_api.messages.
            getByConversationMessageId(peer_id=CHAT_START_ID + storager_chat,
                                       conversation_message_ids=event.message['conversation_message_id']
                                       )['items'][0]['id']
        )

        s.add(user)
        s.commit()

        if answer:
            bot.api.send_chat_msg(event.chat_id, answer)

        return
