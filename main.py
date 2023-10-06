from typing import List

import config
from tasks import init_tasks
from vk_bot.vk_bot import VkBot

from handlers.new_message import new_message
from handlers.events import event_message


from vk_api.bot_longpoll import VkBotEvent

bot = VkBot(config.group_token)


@bot.startup()
def before_start(b: VkBot, *args):
    # b.api.send_chat_msg(config.GUILD_CHAT_ID, 'Ну, я проснулся')
    # All stuff dor startup
    return


@bot.on_stop()
def before_stop(b: VkBot, *args):
    b.api.send_chat_msg(config.GUILD_CHAT_ID, f'Я спать, тыкайте [id{config.creator_id}|его], если что')
    return


@bot.event_handler(event_type='MESSAGE_NEW')
def new_msg(b: bot, e: VkBotEvent):
    return new_message(b, e)


@bot.event_handler('MESSAGE_REPLY')
def dummy(b: bot, e: VkBotEvent):
    # empty def for avoid logs about no handler
    return


@bot.event_handler('MESSAGE_EDIT')
def dummy(b: bot, e: VkBotEvent):
    # empty def for avoid logs about no handler
    return


@bot.event_handler('MESSAGE_EVENT')
def event(b: bot, e: VkBotEvent):
    return event_message(b, e)


@bot.task_check()
def tasks_check(self: VkBot):
    from ORM import session, Task
    from tasks import exec_task
    import datetime

    now = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
    s = session()
    task_list: List[Task] = s.query(Task).all()
    for t in task_list:
        if t.task_when > now:
            continue
        getattr(exec_task, t.task_target)(self, t.task_args)
        s.delete(t)
        s.commit()
    s.close()
    return


@bot.task_init()
def init_task():
    init_tasks()


if __name__ == '__main__':
    bot.start()
    pass
