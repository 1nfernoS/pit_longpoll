import importlib
from typing import Tuple
import os

# import for typing hints
from vk_api.bot_longpoll import VkBotEvent
from vk_bot.vk_bot import VkBot

__all__ = ['command_list', 'Command']


# Here is all allowed commands list
command_list = dict()


class Command:
    def __init__(self, name: str, alias: Tuple[str, ...]):
        self.is_active = None
        self.name = name
        self.alias = alias
        self.desc = 'Empty Command'
        self.set_active(True)
        return

    def get_description(self) -> str:
        return self.desc

    def run(self, bot: VkBot, event: VkBotEvent):
        return

    def set_active(self, state: bool):
        self.is_active = state
        if state:
            command_list[self.alias] = self.__class__
        else:
            command_list.pop(self.alias)
        return

    def __repr__(self):
        return f'Command <{self.name}>'

    def __str__(self):
        return f'<{self.name}>'


for m in [cmd[:-3] for cmd in os.listdir('commands') if not cmd.startswith('__')]:
    module = importlib.import_module('commands.'+m)
    [getattr(module, i)() for i in dir(module)
     if not i.startswith('__') and type(getattr(module, i)) == type and i not in ('Command', 'VkBot', 'VkBotEvent')]

print('\n'.join(f"{i}: {command_list[i]}" for i in command_list))


if __name__ == '__main__':
    pass
