import datetime
from typing import List

from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll

from time import strftime
from requests.exceptions import ReadTimeout

import traceback
import os
from signal import signal, SIGTERM

from vk_bot.vk_methods import VkMethods
from vk_bot.vk_events import VkEvent


class VkBot:
    def __init__(self, token: str) -> None:
        self._events = VkEvent()
        self._token = token

        self._vk = VkApi(token=self._token, api_version='5.131')
        self.api = VkMethods(self._vk.get_api())
        self._name = self.api.get_group_name()
        self._group_id = self.api.group_id()

        self._long_poll = VkBotLongPoll(self._vk, self._group_id, 2)

        self._before_start = None
        self._before_stop = None

        return

    def set_start(self, func: callable):
        self._before_start = func
        return

    def startup(self):
        def wrapper(func: callable):
            self.set_start(func)
            return

        return wrapper

    def set_stop(self, func: callable):
        self._before_stop = func
        signal(SIGTERM, self._before_stop)
        return

    def on_stop(self):
        def wrapper(func: callable):
            self.set_stop(func)
            return

        return wrapper

    def set_handler(self, event_type: str, handler: callable):
        if event_type in self._events.TYPES:
            setattr(self._events, event_type, handler)
        else:
            raise AttributeError(f"{event_type} is not EVENT_TYPE")
        return

    def event_handler(self, event_type: str):
        # decorator for set_handler
        def wrapper(handler: callable, *args, **kwargs):
            self.set_handler(event_type, handler)

        return wrapper

    def start(self):
        from dictionaries.tasks_list import init_tasks
        if self._before_start:
            print('Starting up . . .')
            self._before_start(self)
            print('Started up')

        print(f"[{strftime('%d.%m.%y %H:%M:%S')}] "
              f"Bot {self._name} successfully started! Branch {os.environ.get('BRANCH', 'dev')}\n")

        init_tasks()

        # TODO: Find a proper way to stop bot without "kill -9"
        self._main_loop()

        return

    def _main_loop(self):
        while True:
            try:
                self._event_loop()
                self._tasks_check()
            except KeyboardInterrupt:
                print('\n', 'Stopping . . .', '\n')
                self._before_stop(self) if self._before_stop else None
                return
            except ReadTimeout:
                continue
            except:
                error = traceback.format_exc(-5)
                print(error)
                print(f"\n\n\n\t[{strftime('%d.%m.%y %H:%M:%S')}] Restarting . . .")
                self.api.send_error(f"[{strftime('%d.%m.%y %H:%M:%S')}]\n\n" + error)
                continue
        return

    def _tasks_check(self):
        from ORM import session, Task
        import tasks

        s = session()
        now = datetime.datetime.now()
        task_list: List[Task] = s.query(Task).all()
        for t in task_list:
            if t.task_when > now:
                continue
            getattr(tasks, t.task_target)(self, t.task_args)
            s.delete(t)
            s.commit()
        return

    def _event_loop(self):
        for event in self._long_poll.check():
            # Call def with same name as event type
            getattr(self._events, event.type.name)(self, event)
        return

    def __repr__(self) -> str:
        # Call var
        return f'<VkBot {self._name} (@id-{self._group_id})>'

    def __str__(self) -> str:
        # Call str(var)
        return f'VkBot {self._name}(@id-{self._group_id})'
