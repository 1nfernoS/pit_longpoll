import datetime
import sys

from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll

from requests.exceptions import ReadTimeout

import traceback
import os
import signal

import config
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
        self._tasks_check = None
        self._init_tasks = None
        
        self._loop = True
        if os.name == 'nt':
            signal.signal(signal.SIGTERM, self._exit)
            signal.signal(signal.SIGINT, self._exit)
        if os.name == 'posix':
            signal.signal(signal.SIGQUIT, self._before_stop)
            signal.signal(signal.SIGHUP, self._before_stop)

        return

    def set_start(self, func: callable):
        self._before_start = func
        return

    def startup(self):
        def wrapper(func: callable):
            self.set_start(func)
            return

        return wrapper

    def task_check(self):
        def wrapper(func: callable):
            if config.branch != 'dev':
                self._tasks_check = func
            return

        return wrapper

    def task_init(self):
        def wrapper(func: callable):
            if config.branch != 'dev':
                self._init_tasks = func
            return

        return wrapper

    def set_stop(self, func: callable):
        self._before_stop = func
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
        from tasks import init_tasks
        if self._before_start:
            print('Starting up . . .')
            self._before_start(self)
            print('Started up')

        now = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
        print(f"[{now.strftime('%d.%m.%y %H:%M:%S')}] "
              f"Bot {self._name} successfully started! Branch {os.environ.get('BRANCH', 'dev')}\n")

        if self._init_tasks:
            self._init_tasks()

        # TODO: Find a proper way to stop bot without "kill -9"
        self._main_loop()

        return

    def _main_loop(self):
        while self._loop:
            try:
                self._event_loop()
                if self._tasks_check:
                    self._tasks_check(self)
            except KeyboardInterrupt:
                print('\n', 'Stopping . . .', '\n')
                self._exit()
                continue
            except ReadTimeout:
                continue
            except:
                now = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
                try:
                    etype, value, tb = sys.exc_info()
                    err_msg = ''
                    err_data = traceback.TracebackException(type(value), value, tb, capture_locals=True)
                    for err in err_data.stack[1:]:
                        if 'venv' in err.filename\
                                or 'lib' in err.filename:
                            continue
                        a = {i: err.locals[i] for i in err.locals
                             if not i.startswith('__')
                             and i not in ('error', 'etype', 'tb', 'err_msg')
                             and 'VkBot' not in err.locals[i]
                             and 'vk_api' not in err.locals[i]
                             and 'sqlalchemy' not in err.locals[i]}
                        err_msg += f"{err.filename}:  {err.name}:{err.lineno}\n\t{err.line}"
                        err_msg += f"\nargs: {a}" if a else ""
                        err_msg += "\n" + "=" * 10 + "\n"
                    msg_data = {i: err_data.stack[-1].locals[i].replace(
                        ", 'client_info': {'button_actions': ['text', 'vkpay', 'open_app', 'location', 'open_link', "
                        "'callback', 'intent_subscribe', 'intent_unsubscribe'], 'keyboard': True, 'inline_keyboard': "
                        "True, 'carousel': True, 'lang_id': 0}", "")
                                for i in err_data.stack[-1].locals if 'vk_api' in err_data.stack[-1].locals[i]}
                    err_msg += str(msg_data)

                    now = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
                    err_msg = f"[{now.strftime('%d.%m.%y %H:%M:%S')}] {list(err_data.format_exception_only())[0]}\n" + err_msg

                    print(err_msg)

                    print(f"\n\n\n\t[{now.strftime('%d.%m.%y %H:%M:%S')}] Restarting . . .")
                    self.api.send_error(err_msg)
                except:
                    error = traceback.format_exc(-5)
                    print(error)
                    self.api.send_error(f"[{now.strftime('%d.%m.%y %H:%M:%S')}]\n\n" + error)
                finally:
                    pass
                continue
        return
    
    def _exit(self, *args, **kwargs):
        self._before_stop(self) if self._before_stop else None
        self._loop = False
        return
    
    def _event_loop(self):
        for event in self._long_poll.check():
            # Call def with same name as event type
            getattr(self._events, event.type.name)(self, event)
        return

    def __repr__(self) -> str:
        # Call var
        return f'<VkBot {self._name} (@club-{self._group_id})>'

    def __str__(self) -> str:
        # Call str(var)
        return f'VkBot {self._name}(@club-{self._group_id})'
