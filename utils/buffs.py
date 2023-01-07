from DB.autobuffer_list import load_buffer_buff


BUFF_DATA = load_buffer_buff()

BUFF_RACE = {14413: 'человека', 14414: 'орка', 14415: 'гнома', 14416: 'нежити', 14417: 'эльфа', 14418: 'демона',
             14419: 'гоблина'}

POSSIBLE_ANSWERS = ('через определенное время', 'уже действует', 'Вы не являетесь', 'уже имеющейся', 'наложено другое',
                    'требуется Голос древних')

APOSTOL_ITEM_ID = 14264
WARLOCK_ITEM_ID = 14093
PALADIN_ITEM_ID = 14088
CRUSADER_ITEM_ID = 14256
LIGHT_INC_ITEM_ID = 14257
