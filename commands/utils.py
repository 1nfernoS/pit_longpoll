from commands import Command

from ORM import session, UserInfo, Logs

from config import GUILD_CHAT_ID, GUILD_NAME

from utils.scripts import update_items

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from vk_api.bot_longpoll import VkBotEvent
    from vk_bot.vk_bot import VkBot


class Ping(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('ping', 'пинг', 'тык'))
        self.desc = 'Проверка живой я или нет'
        self.require_basic = True
        # self.set_active(False)
        return

    def run(self, bot: "VkBot", event: "VkBotEvent"):
        s = session()
        user: UserInfo = s.query(UserInfo).filter(UserInfo.user_id == event.message.from_id).first()

        if not user.user_role.role_can_basic:
            return

        Logs(event.message.from_id, __class__.__name__).make_record()

        bot.api.send_chat_msg(event.chat_id, 'Я живой)')
        return


class Grib(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('гриб', 'grib'))
        self.desc = 'Проверка живой я или нет'
        self.require_basic = True
        # self.set_active(False)
        return

    def run(self, bot: "VkBot", event: "VkBotEvent"):
        s = session()
        user: UserInfo = s.query(UserInfo).filter(UserInfo.user_id == event.message.from_id).first()

        if not user.user_role.role_can_basic:
            return

        Logs(event.message.from_id, __class__.__name__).make_record()

        bot.api.send_chat_msg(event.chat_id, '&#127812;')
        return


class War(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('war', 'война'))
        self.desc = 'Список игроков, с которой идет война. Только для членов гильдии'
        self.set_active(False)
        return

    def run(self, bot: "VkBot", event: "VkBotEvent"):
        if event.message.from_id not in bot.api.get_members(GUILD_CHAT_ID):
            war_list = f'Нет, это только для членов гильдии {GUILD_NAME}!'
        else:
            # f"1. Имя Фамилия (расы - класс): &#128481;{attack} &#128737;{defence}
            # &#128074;{strength} &#128400;{agility} &#10084;{endurance} &#127808;{luck}" \
            war_list = "У нас сейчас нет войны с кем-либо!"
        bot.api.send_chat_msg(event.chat_id, war_list)
        return

    @staticmethod
    def __template(bot: "VkBot", event: "VkBotEvent") -> str:
        """
        template generator for run
        :return:
        """
        msg = bot.api.messages.getByConversationMessageId(peer_id=2000000000 + GUILD_CHAT_ID,
                                                          conversation_message_ids=254530)['items'][0]
        res_text = [i['text'] for i in msg['fwd_messages']]
        res_str = ''
        for record in res_text:
            data = record.split('\n')
            name = data[0][24:-2]
            race = data[1][15:]
            class_ = data[2][16:]
            luck = data[5][16:]
            strength = data[6][15:]
            agility = data[7][19:]
            endurance = data[8][22:]
            attack = data[9][14:]
            defence = data[10][16:]
            res_str += f"\n{name} ({race} - {class_}): \n" \
                       f"{attack}:{attack} {defence}:{defence} {luck}:{luck}\n" \
                       f"{strength}:{strength} {agility}:{agility} {endurance}:{endurance}\n"
        return res_str


class Role(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('роль', 'role'))
        self.desc = 'Узнать роль свою или по реплаю'
        self.require_basic = True
        # self.set_active(False)
        return

    def run(self, bot: "VkBot", event: "VkBotEvent"):
        s = session()
        user: UserInfo = s.query(UserInfo).filter(UserInfo.user_id == event.message.from_id).first()

        if not user.user_role.role_can_basic:
            return

        if not user.user_role.role_can_change_role:
            bot.api.send_chat_msg(event.chat_id, f'Ваша роль: {user.user_role.role_name}')
            return

        if 'reply_message' in event.message.keys():
            user_reply: UserInfo = s.query(UserInfo).\
                filter(UserInfo.user_id == event.message.reply_message['from_id']).first()
            answer = f'Роль id{user_reply.user_id}: {user_reply.user_role.role_name}' \
                if user_reply else 'Нет такого пользователя'
            bot.api.send_chat_msg(event.chat_id, answer)
        else:
            bot.api.send_chat_msg(event.chat_id, f'Ваша роль: {user.user_role.role_name}')

        Logs(event.message.from_id, __class__.__name__, None, None,
             event.message.reply_message['from_id']
             if 'reply_message' in event.message.keys()
             else event.message.from_id).make_record()

        return


class Id(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('ид', 'id'))
        self.desc = 'Узнать ид свой или по реплаю. Только для создателя'
        self.require_utils = True
        # self.set_active(False)
        return

    def run(self, bot: "VkBot", event: "VkBotEvent"):
        s = session()

        user: UserInfo = s.query(UserInfo).filter(UserInfo.user_id == event.message.from_id).first()

        if not user.user_role.role_can_utils:
            return

        if 'reply_message' in event.message.keys():
            bot.api.send_chat_msg(event.chat_id, str(event.message.reply_message['from_id']))
            pass
        else:
            bot.api.send_chat_msg(event.chat_id, str(event.message.from_id))

        Logs(event.message.from_id, __class__.__name__, None, None,
             event.message.reply_message['from_id']
             if 'reply_message' in event.message.keys()
             else event.message.from_id).make_record()
        return


class Emoji(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('emoji', 'эмодзи', 'смайл'))
        self.desc = 'Код эмодзи. Только для создателя'
        self.require_utils = True
        # self.set_active(False)
        return

    def run(self, bot: "VkBot", event: "VkBotEvent"):
        s = session()
        user: UserInfo = s.query(UserInfo).filter(UserInfo.user_id == event.message.from_id).first()

        if not user.user_role.role_can_utils:
            return

        Logs(event.message.from_id, __class__.__name__).make_record()

        msg = event.message.text.encode('cp1251', 'xmlcharrefreplace').decode('cp1251')
        msg = msg.split(' ', 1)[1].replace('&#', '').replace(';', '')
        bot.api.send_chat_msg(event.chat_id, msg)
        return


class Bill(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('налоговая',))
        self.desc = 'Списать налог с баланса. Только для казначея'
        self.require_withdraw_bill = True
        # self.set_active(False)
        return

    def run(self, bot: "VkBot", event: "VkBotEvent"):
        s = session()
        user: UserInfo = s.query(UserInfo).filter(UserInfo.user_id == event.message.from_id).first()

        if not user.user_role.role_can_withdraw_bill:
            return

        Logs(event.message.from_id, __class__.__name__).make_record()

        from utils.scripts import withdraw_bill
        withdraw_bill(bot)
        bot.api.send_chat_msg(event.chat_id, f"Списал налог с баланса, проверять можно командой баланс")

        return


class UpdateItems(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('обнови', 'update', 'обновить'))
        self.desc = 'Обновить предметы от А до В. Только для создателя'
        self.require_utils = True
        # self.set_active(False)
        return

    def run(self, bot: "VkBot", event: "VkBotEvent"):
        s = session()
        user: UserInfo = s.query(UserInfo).filter(UserInfo.user_id == event.message.from_id).first()

        if not user.user_role.role_can_utils:
            return

        Logs(event.message.from_id, __class__.__name__).make_record()

        data = event.message.text.split()
        if len(data) < 3:
            return

        if data[1] in ('предметы', 'items'):
            start = data[2]
            stop = data[3]
        else:
            start = data[1]
            stop = data[2]

        bot.api.send_chat_msg(event.chat_id, 'Обновляю предметы, это займет некоторое время и я не буду отвечать...\n'
                                             'Я скажу как закончу')
        update_items(int(start), int(stop))
        bot.api.send_chat_msg(event.chat_id, f'Предметы с {start} по {stop} успешно обновлены и внесены в базу')

        return
