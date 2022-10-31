from commands import Command, command_list

from config import creator_id

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
        else:
            creator = leader = officer = False
        for cmd in command_list:
            if creator:
                message += '[' + ', '.join(cmd) + '] - ' + command_list[cmd].desc + '\n'
            elif leader:
                if not command_list[cmd].require_creator:
                    message += '[' + ', '.join(cmd) + '] - ' + command_list[cmd].desc + '\n'
            elif officer:
                if not command_list[cmd].require_creator and not command_list[cmd].require_leader:
                    message += '[' + ', '.join(cmd) + '] - ' + command_list[cmd].desc + '\n'
            else:
                if not command_list[cmd].require_creator and not command_list[cmd].require_leader and not command_list[cmd].require_officer:
                    message += '[' + ', '.join(cmd) + '] - ' + command_list[cmd].get_description() + '\n'

        message += '\n ПРИМЕЧАНИЕ: После использования, сообщение с командой автоматически удаляется, чтобы уменьшить количество флуда'
        message += f'\n За идеями/ошибками/вопросами обращаться [id{creator_id}|сюда], желательно с приставкой "по котику" или что-то в этом роде'
        bot.api.send_chat_msg(event.chat_id, message)
        return
