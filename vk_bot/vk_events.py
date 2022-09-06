from vk_api.bot_longpoll import VkBotEventType, VkBotEvent



class VkEvent:
    TYPES = [event.name for event in VkBotEventType.mro()[0]]

    def __init__(self):
        for event_type in self.TYPES:
            setattr(self, event_type, self._empty_handler)
        return

    def _empty_handler(self, cls, event: VkBotEvent) -> None:
        print(f"No handler for event {event.type.name}")
        return


if __name__ == '__main__':
    pass
