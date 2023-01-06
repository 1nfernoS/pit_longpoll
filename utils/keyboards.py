import vk_api.keyboard as keyboard

from DB.autobuffer_list import get_buff_command, load_buffer_buff

from utils import buffs


def apostol(vk_id: int, msg_id: int, chat_id: int, race1: int, race2: int = None) -> str:

    kbd = keyboard.VkKeyboard(inline=True)

    for i in buffs.BUFF_DATA[buffs.APOSTOL_ITEM_ID]:
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
    return kbd.get_keyboard()
