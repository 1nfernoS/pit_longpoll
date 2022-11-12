from commands import Command, command_list

from config import COMMISSION_PERCENT, creator_id, GUILD_CHAT_ID

from DB import user_data, users

# import for typing hints
from vk_api.bot_longpoll import VkBotEvent
from vk_bot.vk_bot import VkBot


class Stats(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('stats', 'пинок'))
        self.desc = 'Узнать сколько статов осталось до принудительного перехода на следующий этаж'
        # self.set_active(False)
        return

    def run(self, bot: VkBot, event: VkBotEvent):
        data = user_data.get_user_data(event.message.from_id)
        if data:
            message = f"{data['level']}&#128128;: до пинка {(data['level'] + 15) * 6 - data['strength'] - data['agility']}&#128074;/&#128400; или " \
                      f"{data['level'] * 3 + 45 - data['endurance']}&#10084;"
        else:
            message = "До пинка... Хм... О вас нет записей, покажите профиль хотя бы раз!!"

        bot.api.send_chat_msg(event.chat_id, message)
        return


class Help(Command):

    def __init__(self):
        super().__init__(__class__.__name__, ('помощь', 'команды', 'help'))
        self.desc = 'Список команд'
        # self.set_active(False)
        return

    def run(self, bot: VkBot, event: VkBotEvent):
        message = 'Команды можно вводить как с префиксом, так и без\nВарианты использования - что делает\n'

        data = users.get_user(event.message.from_id)
        if data:
            creator = event.message.from_id == int(creator_id)
            officer = bool(data['is_officer']) if not creator else True
            leader = bool(data['is_leader']) if not creator else True
            guild = event.message.from_id in bot.api.get_members(GUILD_CHAT_ID) if not creator else True
        else:
            creator = leader = officer = guild = False
        for cmd in command_list:
            if creator:
                message += '[' + ', '.join(cmd) + '] - ' + command_list[cmd].desc + '\n'
            elif leader:
                if not command_list[cmd].require_creator:
                    message += '[' + ', '.join(cmd) + '] - ' + command_list[cmd].desc + '\n'
            elif officer:
                if not command_list[cmd].require_creator and not command_list[cmd].require_leader:
                    message += '[' + ', '.join(cmd) + '] - ' + command_list[cmd].desc + '\n'
            elif guild:
                if not command_list[cmd].require_creator and not command_list[cmd].require_leader and not command_list[cmd].require_officer:
                    message += '[' + ', '.join(cmd) + '] - ' + command_list[cmd].desc + '\n'
            else:  # other
                if not command_list[cmd].require_creator and not command_list[cmd].require_leader and not command_list[cmd].require_officer and not command_list[cmd].require_guild:
                    message += '[' + ', '.join(cmd) + '] - ' + command_list[cmd].get_description() + '\n'

        message += '\n ПРИМЕЧАНИЕ: После использования, сообщение с командой автоматически удаляется, чтобы уменьшить количество флуда'
        message += f'\n За идеями/ошибками/вопросами обращаться [id{creator_id}|сюда], желательно с приставкой "по котику" или что-то в этом роде'
        bot.api.send_chat_msg(event.chat_id, message)
        return


class Balance(Command):
    def __init__(self):
        super().__init__(__class__.__name__, ('баланс', 'кошелек', 'деньги', 'balance', 'wallet', 'money'))
        self.desc = 'Узнать свой баланс. Только для членов гильдии'
        self.set_access('guild')
        # self.set_active(False)
        return

    def run(self, bot: VkBot, event: VkBotEvent):
        if event.message.from_id in bot.api.get_members(GUILD_CHAT_ID):
            gold_emoji = '&#127765;'
            balance = users.get_balance(event.message.from_id)
            if balance is not None:
                message = f"Ваш долг: {gold_emoji}{-balance}(Положить {round(-balance/((100-COMMISSION_PERCENT)/100))})" if balance < 0 else f"Сейчас на счету: {gold_emoji}{balance}"
            else:
                message = "Хм... О вас нет записей, покажите профиль хотя бы раз!!"

            bot.api.send_chat_msg(event.chat_id, message)
        return

