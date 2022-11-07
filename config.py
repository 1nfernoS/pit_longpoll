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
IGNORE_LIST = [PIT_BOT, OVERSEER_BOT, 211500453]
ALLOWED_CHATS = [1, 2, 5]

DISCOUNT_PERCENT = 20
COMMISSION_PERCENT = 10


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
