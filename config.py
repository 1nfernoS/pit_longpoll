import os
import json

import prestart
prestart.init()

group_data = json.loads(os.environ.get('GROUP_DATA'))[os.environ.get('BRANCH', 'dev')]
creator_id = os.environ.get('CREATOR_ID')
db_data = json.loads(os.environ.get('DB_DATA'))

PIT_BOT = -182985865
OVERSEER_BOT = -183040898
GUILD_NAME = 'Темная сторона'
GUILD_CHAT_ID = 1
IGNORE_LIST = (PIT_BOT, OVERSEER_BOT, 211500453)
ALLOWED_CHATS = (1, 5, 6)

GUILD_LIBRARIAN_ID = 166287013
GUILD_PAYMASTER_ID = 0

DISCOUNT_PERCENT = 20
COMMISSION_PERCENT = 10

APO_PAYMENT = 100

NOTE_RULES = 'https://vk.com/@asstrickster_kitty-pravila-gildii'
NOTE_ALL = 'https://vk.com/@asstrickster_kitty'

def load(branch: str):
    global group_data
    data = json.loads(os.environ.get('GROUP_DATA'))
    group_data = data.get(branch)
    if group_data:
        os.environ['BRANCH'] = branch
    else:
        group_data = json.loads(os.environ.get('GROUP_DATA'))['dev']
        print(f"No branch '{branch}', loaded 'dev' branch")
    return
