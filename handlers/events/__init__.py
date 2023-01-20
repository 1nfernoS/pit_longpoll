import json

from vk_api.bot_longpoll import VkBotEvent, CHAT_START_ID

from vk_bot.vk_bot import VkBot

from .buffs import buff


def event_message(self: VkBot, event: VkBotEvent):
    pl = event.object.payload
    action = pl.get('action')
    if action:
        if action == 'buff':

            receiver = self.api.get_conversation_msg(
                peer_id=CHAT_START_ID + pl['chat_id'],
                conversation_message_ids=pl['msg_id']
                )['from_id']
            if event.object.user_id != receiver:
                self.api.send_event(
                    event.object.peer_id,
                    event.object.event_id,
                    event.object.user_id,
                    json.dumps({'type': 'show_snackbar', 'text': 'Это не для вас'})
                )
                return

            self.api.send_event(
                event.object.peer_id,
                event.object.event_id,
                event.object.user_id,
                json.dumps({'type': 'show_snackbar', 'text': 'Накладываю бафф...'})
            )

            # TODO in other thread
            res = buff(pl['from'], pl['chat_id'], pl['msg_id'], pl['buff'], receiver)

            self.api.edit_msg(
                event.object.peer_id,
                event.object.conversation_message_id,
                res
            )
            return

        elif action == 'remove':
            self.api.del_msg(
                event.object.peer_id,
                self.api.get_conversation_msg(event.object.peer_id, event.object.conversation_message_id)['id']
            )

            self.api.send_event(
                event.object.peer_id,
                event.object.event_id,
                event.object.user_id,
                json.dumps({'type': 'show_snackbar', 'text': 'Готово!'})
            )
            return

        else:
            self.api.send_event(
                event.object.peer_id,
                event.object.event_id,
                event.object.user_id,
                json.dumps({'type': 'show_snackbar', 'text': 'Что-то пошло не так... Упс?'})
            )
            self.api.del_msg(
                event.object.peer_id,
                self.api.get_conversation_msg(event.object.peer_id, event.object.conversation_message_id)['id']
            )
            return
    else:
        self.api.send_event(
            event.object.peer_id,
            event.object.event_id,
            event.object.user_id,
            json.dumps({'type': 'show_snackbar', 'text': 'Что-то пошло не так... Упс?'})
        )
        self.api.del_msg(
            event.object.peer_id,
            self.api.get_conversation_msg(event.object.peer_id, event.object.conversation_message_id)['id']
        )
        return
    return
