from random import randint
import json

from typing import List
from vk_api.exceptions import ApiError
from vk_api.bot_longpoll import CHAT_START_ID

from config import IGNORE_LIST


def _get_image() -> str:
    """
    :return: with 99.95% chance return kitty emoji, else fox
    """
    return '&#128572;: ' if randint(0, 10000) < 9995 else '&#129418;: '


class VkMethods:

    def __init__(self, api):
        self._api = api

    def send_chat_msg(self, chat_id: int, msg: str, kbd: (dict, None) = None, **kwargs) -> List[dict]:
        msg = _get_image() + msg
        return self._api.messages.send(
            peer_ids=[CHAT_START_ID + chat_id],
            message=msg,
            keyboard=json.dumps(kbd) if kbd else None,
            random_id=0,
            disable_mentions=True,
            **kwargs
        )

    def send_user_msg(self, user_id: int, msg: str, kbd: (dict, None) = None, **kwargs) -> int:
        msg = _get_image() + msg
        return self._api.messages.send(
            peer_id=user_id,
            message=msg,
            keyboard=json.dumps(kbd) if kbd else None,
            random_id=0,
            disable_mentions=True,
            **kwargs
        )

    def edit_msg(self, peer: int, conv_msg_id: int, msg: str, kbd: (dict, None) = None, **kwargs) -> int:
        msg = _get_image() + msg
        return self._api.messages.edit(
            peer_id=peer,
            message=msg,
            conversation_message_id=conv_msg_id,
            disable_mentions=True,
            keyboard=json.dumps(kbd) if kbd else None,
            **kwargs
        )

    def del_msg(self, peer_id: int, msg_id: int) -> int:
        try:
            return self._api.messages.delete(
                peer_id=peer_id,
                message_ids=msg_id,
                delete_for_all=True
            )
        except ApiError:
            return 0

    def send_event(self, peer_id: int, event_id: str, user_id: int, data: dict) -> int:
        return self._api.messages.sendMessageEventAnswer(
            event_id=event_id,
            peer_id=peer_id,
            user_id=user_id,
            event_data=json.dumps(data)
        )

    def pin_msg(self, chat_id: int, conv_msg_id: int, **kwargs) -> int:
        return self._api.messages.pin(
            peer_id=CHAT_START_ID + chat_id,
            conversation_message_id=conv_msg_id
        )

    def get_names(self, list_ids: list, case: str = 'gen') -> str:
        return ', '.join(
            [f"[id{user['id']}|{user['first_name']}]"
             for user in self._api.users.get(user_ids=list_ids, name_case=case)]
        )

    def get_members(self, chat_id: int) -> List[int]:
        return [
            i['member_id']
            for i in self._api.messages.getConversationMembers(peer_id=CHAT_START_ID + chat_id)['items']
            if i['member_id'] not in IGNORE_LIST
        ]

    def kick(self, chat_id: int, user_id: int) -> None:
        try:
            self._api.messages.removeChatUser(
                chat_id=chat_id,
                user_id=user_id
            )
            self.send_chat_msg(chat_id, f"Пользователь @id{user_id} успешно кикнут")
        except ApiError:
            self.send_chat_msg(chat_id, "Ошибка при удалении пользователя")
        return

    def get_group_name(self):
        res = self._api.groups.getById(group_id=0)[0]
        return f"{res['name']} [{res['screen_name']}]"

    def group_id(self):
        return self._api.groups.getById(group_id=0)[0]['id']

    def get_conversation_msg(self, peer_id: int, conversation_message_ids: int) -> dict:
        res = self._api.messages.getByConversationMessageId(peer_id=peer_id, conversation_message_ids=conversation_message_ids)
        return res['items'][0] if res['count'] > 0 else 0
