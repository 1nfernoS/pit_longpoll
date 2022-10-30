import json

from vk_api.bot_longpoll import VkBotEvent

from vk_bot.vk_bot import VkBot


def event_message(self: VkBot, event: VkBotEvent):
    if 'action' in event.message.payload.keys():
        if event.message.payload['action'] == 'test':
            self.api.send_event(
                event.message.event_id,
                event.message.user_id,
                event.message.peer_id,
                json.dumps({'type': 'show_snackbar', 'text': 'Оп оп, пошел процесс'})
            )
            self.api.edit_msg(
                event.message.peer_id,
                event.message.conversation_message_id,
                'Сделано!'
            )
        else:
            self.api.send_event(
                event.message.event_id,
                event.message.user_id,
                event.message.peer_id,
                json.dumps({'type': 'show_snackbar', 'text': 'Что-то пошло не так... Упс?'})
            )
            self.api.del_msg(
                event.message.peer_id,
                self.api.get_conversation_msg(event.message.peer_id, event.message.conversation_message_id)['id']
            )
            pass
    return

