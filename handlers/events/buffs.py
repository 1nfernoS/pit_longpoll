import time

import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll, CHAT_START_ID

from ORM import session
import ORM

from utils.buffs import POSSIBLE_ANSWERS, BUFF_RACE
from utils.emoji import gold

from config import OVERSEER_BOT, APO_PAYMENT


def buff(vk_id: int, chat_id: int, msg_id: int, command: int, receiver: int):
    DB = session()
    buffer: ORM.BuffUser = DB.query(ORM.BuffUser).filter(ORM.BuffUser.buff_user_id == vk_id).first()
    cmd: ORM.BuffCmd = DB.query(ORM.BuffCmd).filter(ORM.BuffCmd.buff_cmd_id == command).first()
    msg = cmd.buff_cmd_text
    if 'race1' in msg:
        msg = msg.replace('race1', BUFF_RACE[buffer.buff_user_race1])
    if 'race2' in msg:
        msg = msg.replace('race2', BUFF_RACE[buffer.buff_user_race2])
    peer = CHAT_START_ID + buffer.buff_user_chat_id

    vk = vk_api.VkApi(token=buffer.buff_user_token, api_version='5.131')
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

    for i in range(3):
        time.sleep(0.5)
        for event in long_poll.check():
            if event.type == VkEventType.MESSAGE_NEW and event.from_group and not event.from_me:
                if not event.peer_id == OVERSEER_BOT:
                    continue
                if not any([msg in event.message for msg in POSSIBLE_ANSWERS]):
                    continue
                return event.message

    res = f"Наложено {msg.lower()}"

    # Change balance
    if buffer.buff_type_id == 14264:
        user_from: ORM.UserInfo = DB.query(ORM.UserInfo).filter(ORM.UserInfo.user_id == receiver).first()
        user_to: ORM.UserInfo = DB.query(ORM.UserInfo).filter(ORM.UserInfo.user_id == buffer.buff_user_id).first()

        if user_from.user_role.role_can_balance:
            user_from.balance -= APO_PAYMENT

        user_to.balance += APO_PAYMENT
        DB.add(user_from)
        DB.add(user_to)

        DB.commit()

        res += f"\n[id{user_from.user_id}|На счету]: {user_from.balance}{gold}"

    return res
