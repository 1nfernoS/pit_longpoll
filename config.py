from typing import Tuple

from os import environ as env
from sys import argv

from json import loads
from dotenv import load_dotenv

# branch-depended
group_token: str = ''
db_data: dict = dict()
# whitelist of chat id's for bot to listen
ALLOWED_CHATS: Tuple[int, ...] = tuple(int(i) for i in env.get('ALLOWED_CHATS').split(','))


def load(branch_name: str):
    if not load_dotenv('.env.' + branch_name):
        print(f"No branch '{branch_name}', loaded 'dev' branch")
        branch_name = 'dev'

    if not load_dotenv('.env.' + branch_name):
        raise EnvironmentError(f'No .env.{branch_name} file')

    global group_token, db_data

    group_token = env.get('group_token')
    db_data = loads(env.get('db_data'))
    return


# Load constants
PIT_BOT: int = -182985865
OVERSEER_BOT: int = -183040898
COMMISSION_PERCENT: int = 10


# load env
if not load_dotenv('.env'):
    raise EnvironmentError('No .env file')


# id's of users in chat but not in guild (bots, guests, etc)
IGNORE_LIST: Tuple[int, ...] = (PIT_BOT, OVERSEER_BOT, *[int(i) for i in env.get('IGNORE').split(',')])

GUILD_NAME: str = env.get('GUILD_NAME')
GUILD_CHAT_ID: int = int(env.get('GUILD_CHAT_ID'))

DISCOUNT_PERCENT: int = int(env.get('PERCENT_DISCOUNT'))

NOTE_RULES: str = env.get('NOTE_RULES')
NOTE_ALL: str = env.get('NOTE_ALL')

APO_PAYMENT: int = int(env.get('PAYMENT_APO'))

creator_id: int = int(env.get('CREATOR_ID'))

branch = env.get('BRANCH')

load(branch)
