import time

import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll, CHAT_START_ID

from DB.autobuffer_list import get_buffer_by_id, get_buff_command, get_peer_by_buffer_id
from DB.users import change_balance, get_balance

from utils.buffs import POSSIBLE_ANSWERS, BUFF_RACE
from utils.emoji import gold

from config import OVERSEER_BOT, APO_PAYMENT


def buff(vk_id: int, chat_id: int, msg_id: int, command: int, receiver: int):
    apo = get_buffer_by_id(vk_id)
    msg = get_buff_command(command)
    if 'race1' in msg:
        msg = msg.replace('race1', BUFF_RACE[apo['race1']])
    if 'race2' in msg:
        msg = msg.replace('race2', BUFF_RACE[apo['race2']])
    peer = CHAT_START_ID + get_peer_by_buffer_id(vk_id, chat_id)

    vk = vk_api.VkApi(token=apo['token_key'], api_version='5.131')
    api = vk.get_api()
    long_poll = VkLongPoll(vk, 1)

    msg_id = api.messages.getByConversationMessageId(
        peer_id=peer,
        conversation_message_ids=msg_id
    )['items'][0]['id']

    api.messages.send(
        peer_ids=[OVERSEER_BOT],
        message=msg,
        random_id=0,
        forward_messages=str(msg_id)
    )

    for i in range(5):
        time.sleep(0.5)
        for event in long_poll.check():
            if event.type == VkEventType.MESSAGE_NEW and event.from_group and not event.from_me:
                if not event.peer_id == OVERSEER_BOT:
                    continue
                if not any([msg in event.message for msg in POSSIBLE_ANSWERS]):
                    continue
                return event.message

    # Change balance
    # if apo['buffer_type'] == 14264:
    #     change_balance(vk_id, APO_PAYMENT)
    #     change_balance(receiver, -APO_PAYMENT)

    res = f"Наложено {msg.lower()}"

    # if apo['buffer_type'] == 14264:
    #     res += f"\n[id{receiver}|На счету]: {get_balance(receiver)}{gold}"
    return res
