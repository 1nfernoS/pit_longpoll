from typing import List

from datetime import datetime as dt

import vk_api.keyboard as keyboard

from ORM import Session, BuffType, BuffCmd

from dictionaries import buffs
from dictionaries.emoji import cancel, clear, heal_trauma, take_trauma

from config import NOTE_ALL, NOTE_RULES


def apostol(vk_id: int, msg_id: int, chat_id: int, race1: int, race2: int = None) -> str:

    kbd = keyboard.VkKeyboard(inline=True)
    DB = Session()
    buffer: BuffType = DB.query(BuffType).filter(BuffType.buff_type_id == buffs.APOSTOL_ITEM_ID).first()
    buffer_commands: List[BuffCmd] = buffer.buff_commands
    for cmd in buffer_commands:

        if cmd.buff_cmd_id == 12:
            if not ((dt.utcnow().date().month == 12
                    and dt.utcnow().date().day > 20)  # from xxx0-12-20
                or (dt.utcnow().date().month == 1
                    and dt.utcnow().date().day < 7)):  # to xxx1-01-07
                continue

        if len(kbd.lines[-1]) // 3 == 1:
            kbd.add_line()

        txt = cmd.buff_cmd_text
        if txt.split()[-1] == 'race1':
            txt = txt.replace('race1', buffs.BUFF_RACE[race1])

        if txt.split()[-1] == 'race2':
            if not race2:
                continue
            txt = txt.replace('race2', buffs.BUFF_RACE[race2])

        payload = {'action': 'buff', 'msg_id': msg_id, 'chat_id': chat_id, 'from': vk_id, 'buff': cmd.buff_cmd_id}
        kbd.add_callback_button(txt.split()[-1].capitalize(), keyboard.VkKeyboardColor.PRIMARY, payload)

    kbd.add_line()
    kbd.add_callback_button(cancel, keyboard.VkKeyboardColor.NEGATIVE, {'action': 'remove'})
    DB.close()
    return kbd.get_keyboard()


def warlock(vk_id: int, msg_id: int, chat_id: int) -> str:

    kbd = keyboard.VkKeyboard(inline=True)
    DB = Session()
    buffer: BuffType = DB.query(BuffType).filter(BuffType.buff_type_id == buffs.WARLOCK_ITEM_ID).first()
    buffer_commands: List[BuffCmd] = buffer.buff_commands

    for cmd in buffer_commands:
        txt = cmd.buff_cmd_text

        payload = {'action': 'buff', 'msg_id': msg_id, 'chat_id': chat_id, 'from': vk_id, 'buff': cmd.buff_cmd_id}
        kbd.add_callback_button(txt.split()[-1].capitalize(), keyboard.VkKeyboardColor.PRIMARY, payload)

    kbd.add_line()
    kbd.add_callback_button(cancel, keyboard.VkKeyboardColor.NEGATIVE, {'action': 'remove'})
    DB.close()
    return kbd.get_keyboard()


def paladin(vk_id: int, msg_id: int, chat_id: int) -> str:

    kbd = keyboard.VkKeyboard(inline=True)
    DB = Session()
    buffer: BuffType = DB.query(BuffType).filter(BuffType.buff_type_id == buffs.PALADIN_ITEM_ID).first()
    buffer_commands: List[BuffCmd] = buffer.buff_commands

    buff = buffer_commands[0].buff_cmd_id
    txt = clear

    payload = {'action': 'buff', 'msg_id': msg_id, 'chat_id': chat_id, 'from': vk_id, 'buff': buff}
    kbd.add_callback_button(txt.split()[-1].capitalize(), keyboard.VkKeyboardColor.PRIMARY, payload)

    kbd.add_line()
    kbd.add_callback_button(cancel, keyboard.VkKeyboardColor.NEGATIVE, {'action': 'remove'})
    DB.close()
    return kbd.get_keyboard()


def crusader(vk_id: int, msg_id: int, chat_id: int) -> str:

    kbd = keyboard.VkKeyboard(inline=True)
    DB = Session()
    buffer: BuffType = DB.query(BuffType).filter(BuffType.buff_type_id == buffs.CRUSADER_ITEM_ID).first()
    buffer_commands: List[BuffCmd] = buffer.buff_commands

    buff = buffer_commands[0].buff_cmd_id
    txt = clear
    payload = {'action': 'buff', 'msg_id': msg_id, 'chat_id': chat_id, 'from': vk_id, 'buff': buff}
    kbd.add_callback_button(txt.split()[-1].capitalize(), keyboard.VkKeyboardColor.PRIMARY, payload)

    buff = buffer_commands[1].buff_cmd_id
    txt = take_trauma
    payload = {'action': 'buff', 'msg_id': msg_id, 'chat_id': chat_id, 'from': vk_id, 'buff': buff}
    kbd.add_callback_button(txt.split()[-1].capitalize(), keyboard.VkKeyboardColor.PRIMARY, payload)

    kbd.add_line()
    kbd.add_callback_button(cancel, keyboard.VkKeyboardColor.NEGATIVE, {'action': 'remove'})
    DB.close()
    return kbd.get_keyboard()


def light_inc(vk_id: int, msg_id: int, chat_id: int) -> str:

    kbd = keyboard.VkKeyboard(inline=True)
    DB = Session()
    buffer: BuffType = DB.query(BuffType).filter(BuffType.buff_type_id == buffs.LIGHT_INC_ITEM_ID).first()
    buffer_commands: List[BuffCmd] = buffer.buff_commands

    buff = buffer_commands[0].buff_cmd_id
    txt = clear
    payload = {'action': 'buff', 'msg_id': msg_id, 'chat_id': chat_id, 'from': vk_id, 'buff': buff}
    kbd.add_callback_button(txt.split()[-1].capitalize(), keyboard.VkKeyboardColor.PRIMARY, payload)

    buff = buffer_commands[1].buff_cmd_id
    txt = heal_trauma
    payload = {'action': 'buff', 'msg_id': msg_id, 'chat_id': chat_id, 'from': vk_id, 'buff': buff}
    kbd.add_callback_button(txt.split()[-1].capitalize(), keyboard.VkKeyboardColor.PRIMARY, payload)

    kbd.add_line()
    kbd.add_callback_button(cancel, keyboard.VkKeyboardColor.NEGATIVE, {'action': 'remove'})
    DB.close()
    return kbd.get_keyboard()


def notes() -> str:
    kbd = keyboard.VkKeyboard(inline=True)

    kbd.add_openlink_button('Правила', NOTE_RULES)
    kbd.add_openlink_button('Все статьи', NOTE_ALL)

    return kbd.get_keyboard()


def announce_restore(note_id: int) -> str:
    kbd = keyboard.VkKeyboard(inline=True)
    kbd.add_button('Восстановить', keyboard.VkKeyboardColor.POSITIVE, {'restore': note_id})
    return kbd.get_keyboard()
