from datetime import datetime
import re
from typing import List, Dict

from config import DISCOUNT_PERCENT

# from DB.items import get_item_by_name, search_item, search_regexp
from ORM import session, Item

from dictionaries import emoji, items


def parse_profile(text: str) -> dict:
    text = text.encode('cp1251', 'xmlcharrefreplace').decode('cp1251')
    officer_emoji = '&#11088;'
    t = text.split('\n')

    id_vk = int(re.findall(r'(?<=id)\d+', t[0])[0])
    name = t[0][:t[0].find(',')].replace('&#128081;', '')

    sep = t[1].find(',')
    class_name = t[1][16:sep]
    DB = session()
    class_item: Item = DB.query(Item).filter(Item.item_name.ilike(f"{class_name}")).first()
    # class_id = get_item_by_name(class_name)
    race = t[1][sep + 1:]

    guild = t[2][18:]
    is_officer = guild.endswith(officer_emoji)
    guild = guild[:-len(officer_emoji)] if is_officer else guild

    level = int(re.findall(r' \d+', t[4])[0])

    strength = int(re.findall(r'(?<=&#128074;)\d+', t[7])[0])
    agility = int(re.findall(r'(?<=&#128400;)\d+', t[7])[0])
    endurance = int(re.findall(r'(?<=&#10084;)\d+', t[7])[0])
    luck = int(re.findall(r'(?<=&#127808;)\d+', t[7])[0])
    attack = int(re.findall(r'(?<=&#128481;)\d+', t[7])[0])
    defence = int(re.findall(r'(?<=&#128737;)\d+', t[7])[0])

    res = {'id_vk': id_vk, 'guild': guild, 'is_officer': is_officer,
           'class_id': class_item.item_id if class_item else None,
           'level': level, 'strength': strength, 'agility': agility, 'endurance': endurance, 'luck': luck,
           'attack': attack, 'defence': defence, 'last_update': datetime.now(), 'class_name': class_name,
           'race': race, 'name': name}
    return res


def parse_storage_action(text: str):
    import profile_api
    text = text.encode('cp1251', 'xmlcharrefreplace').decode('cp1251')

    id_vk = int(re.findall(r'(?<=id)\d+', text)[0])

    if '&#128213;' in text or '&#128216;' in text:
        res = {'item_type': 'book'}

        count = int(re.findall(r'(?<=&#128216;|&#128213;)\d+(?=\*)', text)[0])
        item_name = re.findall(r'(?<=\*)\D+(?=!)', text)[0]
        DB = session()
        item: Item = DB.query(Item).filter(
            Item.item_name.op('regexp')(f"(Книга - |Книга - [[:alnum:]]+ |^[[:alnum:]]+ |^){item_name}.*$"),
            Item.item_has_price == 1).first()
        # item_id = search_item(item_name)['result'][0]['item_id']

        if not item:
            return

        price = profile_api.price(item.item_id)
        result_price = round(price * (100 - DISCOUNT_PERCENT) / 100)
        res.update({'id_vk': id_vk, 'count': count, 'item_name': item_name, 'price': price})

        if 'взяли' in text:
            res['result_price'] = -result_price
        if 'положили' in text:
            res['result_price'] = result_price

    elif 'золота' in text:
        res = {'item_type': 'gold'}

        count = int(re.findall(r'\d+(?= золота)', text)[0])

        if 'взяли' in text:
            res.update({'id_vk': id_vk, 'count': -count})
        if 'положили' in text:
            res.update({'id_vk': id_vk, 'count': count})
    else:
        res = {'item_type': 'item'}
    return res


def guesser(text: str) -> list:
    __possible = items.ingredients_drops
    __possible += items.potions_other
    __possible += items.rings_drops
    __possible += items.materials_raw
    __possible += items.maps
    # other: faith stone
    __possible += [14182]

    text = text.encode('cp1251', 'xmlcharrefreplace').decode('cp1251')
    regexp = text.split('\n')[1].replace(emoji.empty, '[[:alnum:]]')

    DB = session()
    item_list: List[Item] = DB.query(Item).filter(
        Item.item_name.op('regexp')(f"(Книга - |^){regexp}$")).all()
    res = []
    for i in item_list:
        if i.item_id in __possible or '-' in i.item_name:
            res.append(i.item_name.replace('Книга - ', ''))

    return res


def get_elites(text: str) -> int:
    data = text.split('\n')[0]
    count = int(re.findall(r'(?<=\()\d+(?=\))', data)[0])
    return count


def get_siege(text: str) -> Dict[str, str]:
    data = text.split('\n')
    name = data[0].split('Вы успешно присоединились к осадному лагерю гильдии')[-1].strip()
    role = re.findall(r'(?<=\(\+)\d+&#\d+;(?=\))', data[1])[0]
    res = {
        'name': name,
        'role': role
    }
    return res


if __name__ == '__main__':
    sample = '&#128081;[id16191014|Юрий], Ваш профиль: | &#128100;Класс: клинок тьмы, человек-эльф | &#128101;Гильдия: Темная сторона | &#128578;Положительная карма | &#128128;Уровень: 90 | &#127881;Достижений: 32 | &#127765;Золото: 24819 | &#128074;295 &#128400;303 &#10084;314 &#127808;21 &#128481;107 &#128737;90'
    result = parse_profile(sample.replace(' | ', '\n'))
    print(result)
    pass
