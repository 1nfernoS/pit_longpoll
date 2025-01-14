from config import GUILD_CHAT_ID

from .buttons import payloads

from ORM import Session, UserInfo, UserStats, Item, Logs, BuffUser

from profile_api import get_profile, get_books

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from vk_bot.vk_bot import VkBot
    from vk_api.bot_longpoll import VkBotEvent


def user_message(self: "VkBot", event: "VkBotEvent"):

    if 'payload' in event.message.keys():
        payloads(self, event)
        return

    # direct message from user
    if len(event.message.attachments) != 0:
        at = event.message.attachments[0]
        if at['type'] == 'link':
            if event.message.text == "":
                event.message.text = at['link']['url']

    if event.message.text.lower().startswith('/buffer'):
        reg_pit_buffer(self, event)
        return

    if 'https://vip3.activeusers.ru/app.php?' in event.message.text:
        reg_pit_profile(self, event)
        return
    return


def reg_pit_profile(self: "VkBot", event: "VkBotEvent"):
    if event.message.from_id not in self.api.get_members(GUILD_CHAT_ID):
        ans = "Я надеюсь, ты понимаешь, что только что предоставил ПОЛНЫЙ доступ к своему профилю?\n" \
              "Ладно уж, я в него не полезу, но лучше так больше не делай"
        self.api.send_user_msg(event.message.from_id, ans)
        return

    Logs(event.message.from_id,
         'Profile_link'
         ).make_record()

    ans = 'Пару секунд, мне нужно изучить твои статы и экипировку...'
    self.api.send_user_msg(event.message.from_id, ans)

    s = event.message.text[event.message.text.find('act='):event.message.text.find('&group_id')]
    auth = s[s.find('auth_key') + 9:s.find('auth_key') + 41]
    profile = get_profile(auth, event.message.from_id)

    DB = Session()

    inv = [int(i) for i in profile['items']]
    class_id = inv[0] if inv[0] != 14108 else inv[1]
    class_name: Item = DB.query(Item).filter(Item.item_id == class_id).first()
    build = get_books(inv)

    stats = profile['stats']
    new_data = (class_id,
                stats['level'], stats['attack'], stats['defence'],
                stats['strength'], stats['agility'], stats['endurance'],
                stats['luck'], stats['accuracy'], stats['concentration'])
    info: UserInfo = DB.query(UserInfo).filter(UserInfo.user_id == event.message.from_id).first()

    if info:
        info.user_profile_key = auth

        info.user_items = [DB.query(Item).filter(Item.item_id == i).first()
                           for i in build]
        stats: UserStats = info.user_stats
        stats.class_id, stats.user_level, stats.user_attack, stats.user_defence, stats.user_strength, \
            stats.user_agility, stats.user_endurance, stats.user_luck, stats.user_accuracy, \
            stats.user_concentration = new_data

        ans = f"Обновил твой профиль! Значит, твой высший класс {class_name.item_name}?\n" \
              f"Похвально, я буду сообщать о тебе, когда твои книги будут на продаже"
    else:
        info = UserInfo()
        stats = UserStats()

        info.user_id = event.message.from_id
        info.user_profile_key = auth
        info.user_items = [DB.query(Item).filter(Item.item_id == i).first()
                           for i in build]

        stats.user_id = event.message.from_id
        stats.class_id, stats.user_level, stats.user_attack, stats.user_defence, stats.user_strength, \
            stats.user_agility, stats.user_endurance, stats.user_luck, stats.user_accuracy, \
            stats.user_concentration = new_data

        ans = f"В первый раз, значит? Что ж, проходи, сейчас запишу... \n" \
              f"Так, высший класс {class_name.item_name}, хорошо...\n" \
              f"Готово, теперь я буду сообщать о тебе, когда твои книги будут на продаже"

    DB.add(info)
    DB.add(stats)
    DB.commit()
    DB.close()
    self.api.send_user_msg(event.message.from_id, ans)
    return


def reg_pit_buffer(self: "VkBot", event: "VkBotEvent"):
    links = event.message.text.split()[1:]
    vk_data, pit_data = None, None

    msg_pit_err = 'Не могу найти ссылку на профиль колодца... Точно указал как в статье а не приложение вк?'
    if 'oauth.vk.com' in links[0]:
        vk_data = extract_url(links[0])
        if 'vip3.activeusers.ru/app.php' in links[1]:
            pit_data = extract_url(links[1])
        else:
            self.api.send_user_msg(event.message.from_id, msg_pit_err)
            return
    elif 'oauth.vk.com' in links[1]:
        vk_data = extract_url(links[1])
        if 'vip3.activeusers.ru/app.php' in links[0]:
            pit_data = extract_url(links[0])
        else:
            self.api.send_user_msg(event.message.from_id, msg_pit_err)
            return
    else:
        msg = 'Не могу найти ссылку с токеном вк... Точно скопировал ее целиком?'
        self.api.send_user_msg(event.message.from_id, msg)
        return

    if not pit_data['viewer_id'] == vk_data['user_id'] == str(event.message.from_id):
        self.api.send_user_msg(event.message.from_id, 'Что-то не сходится... Какая-то из ссылок не о тебе')
        return

    Logs(event.message.from_id,
         'Profile_link',
         'Reg Apo'
         ).make_record()

    from profile_api import get_races, get_buff_class

    class_id = get_buff_class(pit_data['auth_key'], pit_data['viewer_id'])
    if not class_id:
        self.api.send_user_msg(event.message.from_id, 'Ты дал мне ПОЛНЫЙ доступ к ВК и Колодцу, не имея класс '
                                                      'способный накладывать заклинания? \nЯ закрою глаза и забуду, '
                                                      'но лучше так не делай')
        return

    races = get_races(pit_data['auth_key'], pit_data['viewer_id'])
    try:
        race1, race2 = races
    except ValueError:
        race1, race2 = races[0], None

    from utils.scripts import get_chat_id
    chat_id = get_chat_id(vk_data['access_token'])

    DB = Session()
    buffer: BuffUser = DB.query(BuffUser).filter(BuffUser.buff_user_id == event.message.from_id).first()
    if not buffer:
        buffer = BuffUser(vk_data['user_id'], True,
                          pit_data['auth_key'], vk_data['access_token'],
                          class_id, race1, race2, chat_id)
    else:
        buffer.buff_user_is_active = True
        buffer.buff_user_token = vk_data['access_token']
        buffer.buff_user_profile_key = pit_data['auth_key']
        buffer.buff_type_id = class_id
        buffer.buff_user_race1 = race1
        buffer.buff_user_race2 = race2
        buffer.buff_user_chat_id = chat_id
    DB.add(buffer)
    DB.commit()
    DB.close()

    self.api.send_user_msg(event.message.from_id, 'Отлично, теперь ты один из бафферов!')
    return


def extract_url(url: str) -> dict:
    if '#' in url:
        args = url[url.find('#') + 1:]
    elif '?' in url:
        args = url[url.find('?') + 1:]
    else:
        raise RuntimeError('Can\'t find symbol to parse link')
    return {i.split('=')[0]: i.split('=')[1] for i in args.split('&')}
