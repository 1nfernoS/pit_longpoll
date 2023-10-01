"""
Module of def which calls from task list from DB
They are just executes only with data, not creates task
"""

import datetime
import json

from config import GUILD_CHAT_ID, LEADER_CHAT_ID
from utils.scripts import withdraw_bill, check_elites, check_siege_report
from dictionaries import emoji as e

from ORM import Task

# import for typing hints
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from vk_bot.vk_bot import VkBot


def remind(bot: "VkBot", data: str):
    __keys = ('user_id', 'text', 'msg_id')
    data = json.loads(data)
    if not all(key in data for key in __keys):
        raise ValueError(f"Task doesn't have enough/valid arguments to run ({data})")
    msg = f"@id{data['user_id']}(Напоминаю) {data['text']}"
    bot.api.send_chat_msg(GUILD_CHAT_ID, msg, disable_mentions=False,
                          reply_to=data['msg_id'])
    return


# weekly
def siege(bot: "VkBot", data: str = None):
    data = check_siege_report(bot)
    names = {i[0]: i[1] for i in zip(data.keys(), bot.api.get_names(list(data.keys()), 'nom').split(', '))}

    statistics = {'reported': 0, 'not_reported': 0}

    msg = f"Статистика по осаде {datetime.date.today().strftime('%d.%m.%Y')}\n\n"
    for user_id in data:
        name = names[user_id]
        msg += f"{e.check if data[user_id] else e.cancel}{name}\n"
        if data[user_id]:
            statistics['reported'] += 1
        else:
            statistics['not_reported'] += 1

    msg += f"\n{e.check}: {statistics['reported']}; {e.cancel}: {statistics['not_reported']}"

    bot.api.send_chat_msg(LEADER_CHAT_ID, msg)

    next_run = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
    next_run = next_run.replace(hour=22, minute=5, second=0)
    next_run += datetime.timedelta(days=7 if next_run.isoweekday() == 3 else ((7 + 3 - next_run.isoweekday()) % 7))

    Task(next_run, siege, is_regular=True).add()
    return


# half-monthly
def bill(bot: "VkBot", data: str = None):
    msg = 'Сегодня будет списан налог!\nВсе дружно написали "мой профиль" и "баланс" (без кавычек)\n\n@all'
    bot.api.send_chat_msg(GUILD_CHAT_ID, msg, disable_mentions=False)

    month = datetime.datetime.utcnow().month % 12 + 1
    next_run = datetime.datetime.utcnow().replace(day=15, month=month, hour=10, minute=30, second=0)
    Task(next_run, bill, is_regular=True).add()
    return


# for avoiding name crossing
def bill2(bot: "VkBot", data: str = None):
    msg = 'Сегодня будет списан налог!\nВсе дружно написали "мой профиль" и "баланс" (без кавычек)\n\n@all'
    bot.api.send_chat_msg(GUILD_CHAT_ID, msg, disable_mentions=False)

    month = datetime.datetime.utcnow().month % 12 + 1
    next_run = datetime.datetime.utcnow().replace(day=1, month=month, hour=10, minute=30, second=0)
    Task(next_run, bill2, is_regular=True).add()
    return


# monthly
def elites(bot: "VkBot", data: str = None):
    data = check_elites(bot)

    statistics = {'overlimit': 0, 'limit': 0, 'underlimit': 0, 'none': 0}

    month = '{:0>2}'.format((datetime.date.today().month + 10) % 12 + 1)
    year = datetime.date.today().year if datetime.date.today().month > 1 else datetime.date.today().year - 1
    msg = f"Статистика по сдаче элитных трофеев за {month}.{year}\n\n"

    names = {i[0]: i[1] for i in zip(data.keys(), bot.api.get_names(list(data.keys()), 'nom').split(', '))}

    for user_id in data:

        name = names[user_id]
        level = data[user_id]['level']
        elite = data[user_id]['elites']
        limit = data[user_id]['limit']

        msg += f"{e.cancel if elite < limit else e.check}{name} ({level}): {elite}/{limit}{e.elite_trophy}\n"

        if elite > limit:
            statistics['overlimit'] += 1
        elif elite == limit:
            statistics['limit'] += 1
        elif elite == 0:
            statistics['none'] += 1
        elif elite < limit:
            statistics['underlimit'] += 1

    msg += f"\nИтого\nСдали сверх нормы: {statistics['overlimit']}\nСдали ровно: {statistics['limit']}" \
           f"\nНе добрали: {statistics['none']}\nНе сдали ничего: {statistics['underlimit']}"

    bot.api.send_chat_msg(LEADER_CHAT_ID, msg)

    month = datetime.datetime.utcnow().month % 12 + 1
    next_run = datetime.datetime.now().replace(day=2, month=month, hour=12, minute=30, second=0)

    Task(next_run, elites, is_regular=True).add()
    return