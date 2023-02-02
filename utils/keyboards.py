import vk_api.keyboard as keyboard

from DB.autobuffer_list import get_buff_command

from utils import buffs
from utils.emoji import cancel, clear, heal_trauma, take_trauma

from config import NOTE_ALL, NOTE_RULES


def apostol(vk_id: int, msg_id: int, chat_id: int, race1: int, race2: int = None) -> str:

    kbd = keyboard.VkKeyboard(inline=True)

    for i in buffs.BUFF_DATA[buffs.APOSTOL_ITEM_ID]:

        if i == 12:
            continue

        if len(kbd.lines[-1]) // 3 == 1:
            kbd.add_line()

        txt = get_buff_command(i)
        if txt.split()[-1] == 'race1':
            txt = txt.replace('race1', buffs.BUFF_RACE[race1])

        if txt.split()[-1] == 'race2':
            if not race2:
                continue
            txt = txt.replace('race2', buffs.BUFF_RACE[race2])

        payload = {'action': 'buff', 'msg_id': msg_id, 'chat_id': chat_id, 'from': vk_id, 'buff': i}
        kbd.add_callback_button(txt.split()[-1].capitalize(), keyboard.VkKeyboardColor.PRIMARY, payload)

    kbd.add_line()
    kbd.add_callback_button(cancel, keyboard.VkKeyboardColor.NEGATIVE, {'action': 'remove'})

    return kbd.get_keyboard()


def warlock(vk_id: int, msg_id: int, chat_id: int) -> str:

    kbd = keyboard.VkKeyboard(inline=True)

    for i in buffs.BUFF_DATA[buffs.WARLOCK_ITEM_ID]:
        txt = get_buff_command(i)

        payload = {'action': 'buff', 'msg_id': msg_id, 'chat_id': chat_id, 'from': vk_id, 'buff': i}
        kbd.add_callback_button(txt.split()[-1].capitalize(), keyboard.VkKeyboardColor.PRIMARY, payload)

    kbd.add_line()
    kbd.add_callback_button(cancel, keyboard.VkKeyboardColor.NEGATIVE, {'action': 'remove'})

    return kbd.get_keyboard()


def paladin(vk_id: int, msg_id: int, chat_id: int) -> str:

    kbd = keyboard.VkKeyboard(inline=True)

    buff = buffs.BUFF_DATA[buffs.PALADIN_ITEM_ID][0]
    txt = clear

    payload = {'action': 'buff', 'msg_id': msg_id, 'chat_id': chat_id, 'from': vk_id, 'buff': buff}
    kbd.add_callback_button(txt.split()[-1].capitalize(), keyboard.VkKeyboardColor.PRIMARY, payload)

    kbd.add_line()
    kbd.add_callback_button(cancel, keyboard.VkKeyboardColor.NEGATIVE, {'action': 'remove'})

    return kbd.get_keyboard()


def crusader(vk_id: int, msg_id: int, chat_id: int) -> str:

    kbd = keyboard.VkKeyboard(inline=True)

    buff = buffs.BUFF_DATA[buffs.CRUSADER_ITEM_ID][0]
    txt = clear
    payload = {'action': 'buff', 'msg_id': msg_id, 'chat_id': chat_id, 'from': vk_id, 'buff': buff}
    kbd.add_callback_button(txt.split()[-1].capitalize(), keyboard.VkKeyboardColor.PRIMARY, payload)

    buff = buffs.BUFF_DATA[buffs.CRUSADER_ITEM_ID][1]
    txt = take_trauma
    payload = {'action': 'buff', 'msg_id': msg_id, 'chat_id': chat_id, 'from': vk_id, 'buff': buff}
    kbd.add_callback_button(txt.split()[-1].capitalize(), keyboard.VkKeyboardColor.PRIMARY, payload)

    kbd.add_line()
    kbd.add_callback_button(cancel, keyboard.VkKeyboardColor.NEGATIVE, {'action': 'remove'})

    return kbd.get_keyboard()


def light_inc(vk_id: int, msg_id: int, chat_id: int) -> str:

    kbd = keyboard.VkKeyboard(inline=True)

    buff = buffs.BUFF_DATA[buffs.LIGHT_INC_ITEM_ID][0]
    txt = clear
    payload = {'action': 'buff', 'msg_id': msg_id, 'chat_id': chat_id, 'from': vk_id, 'buff': buff}
    kbd.add_callback_button(txt.split()[-1].capitalize(), keyboard.VkKeyboardColor.PRIMARY, payload)

    buff = buffs.BUFF_DATA[buffs.LIGHT_INC_ITEM_ID][1]
    txt = heal_trauma
    payload = {'action': 'buff', 'msg_id': msg_id, 'chat_id': chat_id, 'from': vk_id, 'buff': buff}
    kbd.add_callback_button(txt.split()[-1].capitalize(), keyboard.VkKeyboardColor.PRIMARY, payload)

    kbd.add_line()
    kbd.add_callback_button(cancel, keyboard.VkKeyboardColor.NEGATIVE, {'action': 'remove'})

    return kbd.get_keyboard()


def notes() -> str:
    kbd = keyboard.VkKeyboard(inline=True)

    kbd.add_openlink_button('Правила', NOTE_RULES)
    kbd.add_openlink_button('Все статьи', NOTE_ALL)

    return kbd.get_keyboard()
