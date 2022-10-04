from commands import Command, command_list

from DB.user_data import get_user_data

# import for typing hints
from vk_api.bot_longpoll import VkBotEvent
from vk_bot.vk_bot import VkBot


class Stats(Command):

    desc = 'Узнать сколько статов осталось до насильного перехода на следующий этаж'

    def __init__(self):
        super().__init__(__class__.__name__, ('статы', 'stats', 'пинок'))
        # self.set_active(False)
        return

    def run(self, bot: VkBot, event: VkBotEvent):
        data = get_user_data(event.message.from_id)
        if data:
            message = f"{data['level']}&#128128;: до пинка {(data['level'] + 15) * 6 - data['strength'] - data['agility']}&#128074;/&#128400; или " \
                      f"{data['level'] * 3 + 45 - data['endurance']}&#10084;"
        else:
            message = "До пинка... Хм... О вас нет записей, покажите профиль хотя бы раз!!"

        bot.api.send_chat_msg(event.chat_id, message)
        return


class Help(Command):

    desc = 'Список команд'

    def __init__(self):
        super().__init__(__class__.__name__, ('помощь', 'команды', 'help'))
        # self.set_active(False)
        return

    def run(self, bot: VkBot, event: VkBotEvent):
        message = 'Команды можно вводить как с префиксом, так и без\nВарианты использования - что делает\n'
        for cmd in command_list:
            message += '[' + ', '.join(cmd) + '] - ' + command_list[cmd].get_description(command_list[cmd]) + '\n'

        bot.api.send_chat_msg(event.chat_id, message)
        return

