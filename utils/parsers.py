from datetime import datetime, timedelta
import re
from typing import List, Dict

from config import DISCOUNT_PERCENT

from ORM import session, Item

from dictionaries import emoji, items


def parse_profile(text: str) -> dict:
    text = text.encode('cp1251', 'xmlcharrefreplace').decode('cp1251')
    officer_emoji = '&#11088;'
    t = text.split('\n')

    id_vk = int(re.findall(r'(?<=id)\d+', t[0])[0])
    name = re.findall(r'(?<=\|)[\s\w]+(?=])', t[0])[0]

    class_name = re.findall(r'(?<=:)[\w\s]+(?=, | \()', t[1])[0].strip()

    race = re.findall(r'(?<=,)[\w\s-]+', t[1])[0].strip()

    guild = re.findall(r'(?<=:)[\s\w]+', t[2])[0].strip()
    is_officer = officer_emoji in t[2]

    karma = re.findall(r'&#\d+;', t[3])[0]

    level = int(re.findall(r'(?<=: )\d+', t[4])[0])

    achievements = int(re.findall(r'(?<=: )\d+', t[5])[0])

    gold = int(re.findall(f'(?<={emoji.gold})\\d+', t[6])[0])
    scatter = int(re.findall(f'(?<={emoji.scatter})\\d+', t[6])[0])

    strength = int(re.findall(r'(?<=&#128074;)\d+', t[7])[0])
    agility = int(re.findall(r'(?<=&#128400;)\d+', t[7])[0])
    endurance = int(re.findall(r'(?<=&#10084;)\d+', t[7])[0])
    luck = int(re.findall(r'(?<=&#127808;)\d+', t[7])[0])
    attack = int(re.findall(r'(?<=&#128481;)\d+', t[7])[0])
    defence = int(re.findall(r'(?<=&#128737;)\d+', t[7])[0])

    DB = session()
    class_item: Item = DB.query(Item).filter(Item.item_name.ilike(f"{class_name}")).first()
    DB.close()

    res = {
        'id_vk': id_vk, 'name': name,
        'class_id': class_item.item_id if class_item else None, 'class_name': class_name, 'race': race,
        'guild': guild, 'is_officer': is_officer, 'karma': karma, 'level': level, 'achievements': achievements,
        'gold': gold, 'scatter': scatter, 'strength': strength, 'agility': agility, 'endurance': endurance,
        'luck': luck, 'attack': attack, 'defence': defence,
        'last_update': datetime.utcnow() + timedelta(hours=3)
    }
    return res


def parse_storage_action(text: str):
    import profile_api
    text = text.encode('cp1251', 'xmlcharrefreplace').decode('cp1251')

    id_vk = int(re.findall(r'(?<=id)\d+', text)[0])

    if '&#128213;' in text or '&#128216;' in text:
        res = {'item_type': 'book'}

        count = int(re.findall(r'(?<=&#128216;|&#128213;)\d+(?=\*)', text)[0])
        item_name = re.findall(r'(?<=\*)\D+(?=!)', text)[0]
        with session() as DB:
            item: Item = DB.query(Item).filter(
                Item.item_name.op('regexp')(f"(Книга - |Книга - [[:alnum:]]+ |^[[:alnum:]]+ |^){item_name}.*$"),
                Item.item_has_price == 1).first()

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
    DB.close()
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


def get_transfer(text: str) -> Dict[str, str]:
    text = text.encode('cp1251', 'xmlcharrefreplace').decode('cp1251')
    from dictionaries.emoji import gold, item

    data = {'type': 'gold' if gold in text else 'item' if item in text else 'other',
            'user_from': (re.findall(r'\[id\d+\|[^]]+]', text))[1],
            'user_to': (re.findall(r'\[id\d+\|[^]]+]', text))[0],
            'id_from': ([int(i) for i in re.findall(r'(?<=id)\d+', text)])[1],
            'id_to': ([int(i) for i in re.findall(r'(?<=id)\d+', text)])[0]}

    # TODO: check other cases

    if data['type'] == 'item':
        text = text.replace(item, '')
        item_name = re.findall(r'(?<=;).+(?= от игрока)', text)[0]
        count = re.findall(r'\d+(?=\*)', item_name)
        item_name = re.findall(r'(?<=\*).+', item_name)[0] if '*' in item_name else item_name
        count = int(count[0]) if count else 1
        data['count'] = count
        data['item_name'] = item_name

    if data['type'] == 'gold':
        data['count'] = int(re.findall(r'\d+(?= золота)', text)[0])
        data['item_name'] = 'золото'

    return data


def parse_cross_signs(text: str) -> str:
    from dictionaries.puzzle_answers import cross_answers

    keys = re.findall(r'\b(?<=\")([^\"]+)(?=\")', text.lower())
    data1, data2 = cross_answers.get(keys[0], 'Неизвестно').split(','), cross_answers.get(keys[1], 'Неизвестно').split(
        ',')
    res = []
    for a in data1:
        if a in data2:
            res.append(a)
    return ', '.join(res) if res else ', '.join(set(data1 + data2))


def parse_time(text: str) -> timedelta:
    h = re.findall(r'\d+(?=\s*час\D)', text)
    m = re.findall(r'\d+(?=\s*мин\D)', text)
    s = re.findall(r'\d+(?=\s*сек\D)', text)
    return timedelta(hours=int(h[0]) if h else 0, minutes=int(m[0]) if m else 0, seconds=int(s[0]) if s else 0)


def fishing(messages: List[str]) -> dict:
    messages = [msg['text'].encode('cp1251', 'xmlcharrefreplace').decode('cp1251') for msg in messages]
    result = {'bait': 0, 'fish_trophy': 0, 'food': 0,
              'loot': {'shell': 0, 'oil': 0, 'other': []},
              'trophy': 0, 'gold': 0, 'scatter': 0, 'unknown': []}

    for msg in messages:
        if emoji.cancel in msg:
            break
        if '&#128683;' in msg:
            continue
        if emoji.bait in msg:
            result['bait'] += 1
            continue
        if emoji.sell_fish in msg:
            result['fish_trophy'] += int(re.findall(r'(?<=\s)\d+(?=\s)', msg)[0])
            continue
        if emoji.food_fish in msg:
            result['food'] += 1
            continue
        if emoji.shell in msg:
            result['loot']['shell'] += 1
            continue
        if 'рыбий жир' in msg.lower():
            result['loot']['oil'] += 1
            continue
        if emoji.scatter in msg.lower():
            result['scatter'] += 1
            continue
        if emoji.level in msg:
            result['trophy'] += int(re.findall(r'(?<=\s)\d+(?=\s)', msg.split('\n\n')[1])[0])
        if emoji.item in msg:
            if 'продан' in msg:
                result['gold'] += int(re.findall(r'(?<=\s)\d+(?=\s)', msg.split('\n\n')[-1])[0])
            else:
                result['loot']['other'] += re.findall(r'(?<=;)[\w\s]+(?=!)', msg.split('\n\n')[-1])
            continue
        result['unknown'].append(msg)
    return result


def ruins_parse(messages: List[str]) -> dict:
    messages = [msg['text'].encode('cp1251', 'xmlcharrefreplace').decode('cp1251') for msg in messages]
    result = {'loot': [],
              'trophy': 0, 'gold': 0, 'scatter': 0, 'unknown': []}

    for msg in messages:
        if emoji.cancel in msg or 'Прервать поиск' in msg:
            break
        if emoji.wait in msg:
            continue
        if emoji.scatter in msg.lower():
            result['scatter'] += 1
            continue
        if emoji.level in msg:
            result['trophy'] += int(re.findall(r'(?<=\s)\d+(?=\s)', msg.split('\n\n')[0])[0])
        if emoji.item in msg:
            if 'продан' in msg:
                result['gold'] += int(re.findall(r'(?<=\s)\d+(?=\s)', msg.split('\n\n')[-1])[0])
            else:
                result['loot'] += re.findall(r'(?<=;)[\w\s-]+(?=!)', msg.split('\n\n')[-1])
            continue
        result['unknown'].append(msg)
    return result


if __name__ == '__main__':
    sample = '&#128081;[id16191014|Юрий], Ваш профиль: | &#128100;Класс: клинок тьмы, человек-эльф | &#128101;Гильдия: Темная сторона | &#128578;Положительная карма | &#128128;Уровень: 90 | &#127881;Достижений: 32 | &#127765;Золото: 24819 | &#128074;295 &#128400;303 &#10084;314 &#127808;21 &#128481;107 &#128737;90'
    result = parse_profile(sample.replace(' | ', '\n'))
    print(result)
    pass
