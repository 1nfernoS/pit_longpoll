from datetime import datetime

from DB.items import get_item_by_name


def parse_profile(text: str) -> dict:
    text = text.encode('cp1251', 'xmlcharrefreplace').decode('cp1251')
    import re
    officer_emoji = '&#11088;'
    t = text.split('\n')

    id_vk = int(re.findall(r'(?<=id)\d+', t[0])[0])
    name = t[0][:t[0].find(',')].replace('&#128081;', '')

    sep = t[1].find(',')
    class_name = t[1][16:sep]
    class_id = get_item_by_name(class_name)
    race = t[1][sep+1:]

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

    res = {'id_vk': id_vk, 'guild': guild, 'is_officer': is_officer, 'class_id': class_id if class_id else None,
           'level': level, 'strength': strength, 'agility': agility, 'endurance': endurance, 'luck': luck,
           'attack': attack, 'defence': defence, 'last_update': datetime.now(), 'class_name': class_name,
           'race': race, 'name': name}
    return res
