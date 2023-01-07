import json

from vk_api.bot_longpoll import VkBotEvent

from vk_bot.vk_bot import VkBot

from .buffs import buff


def event_message(self: VkBot, event: VkBotEvent):
    pl = event.object.payload
    action = pl.get('action')
    if action:
        if action == 'buff':
            if event.object.user_id != pl['from']:
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
            res = buff(pl['from'], pl['chat_id'], pl['msg_id'], pl['buff'])

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
