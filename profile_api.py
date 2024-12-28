import requests
import json

from typing import List, Union, Dict

from bs4 import BeautifulSoup

from dictionaries import items


# TODO: Refactor for urllib
def get_name(item_id: int) -> str:
    url = f'https://vip3.activeusers.ru/app.php?act=item&id={item_id}&auth_key=5153d58b92d71bda47f1dac05afc187a&viewer_id=158154503&group_id=182985865&api_id=7055214'
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    try:
        return soup.find_all('div', class_='shop_res-title')[0].contents[0].strip()
    except:
        return ''


def lvl_skills(auth_key: str, user_id: int) -> Dict[str, Dict[str, int]]:
    import re
    url = f'https://vip3.activeusers.ru/app.php?act=pages&id=702&auth_key={auth_key}&viewer_id={user_id}&group_id=182985865&api_id=7055214'

    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    a = soup.body.find_all('div', {'class': 'element-box'})[0]
    active, passive = a.find_all('p')
    p_level = {i.split(':')[0]: int(re.findall(r'\d+', i.split(':')[1])[0]) for i in passive.get_text().split('\n')}
    a_level = {i.split(':')[0]: int(re.findall(r'\d+', i.split(':')[1])[0]) for i in active.get_text().split('\n')}
    return {'active': a_level, 'passive': p_level}

def lvl_active(auth_key: str, user_id: int) -> Dict[str, List[Union[int, float]]]:
    url = f'https://vip3.activeusers.ru/app.php?act=pages&id=620&auth_key={auth_key}&viewer_id={user_id}&group_id=182985865&api_id=7055214'

    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    t_res = soup.body.find_all('div', class_='portlet-body')[0]
    res_dict = dict()

    for i in t_res.find_all('li'):
        z = list()
        for j in i.text.split():
            if j.endswith(':'):
                item = ' '.join(i.text.split()[:i.text.split().index(j) + 1])
                z.append(item.replace(':', '').replace('.', ''))
            if j.isdigit():
                z.append(int(j))
                z.append((round((int(j) / 10) ** 0.5 * 10) + 100) / 100)
        res_dict[z[0]] = [z[1], z[2]]
    return res_dict


def lvl_passive(auth_key: str, user_id: int) -> Dict[str, List[Union[int, float]]]:
    url = f'https://vip3.activeusers.ru/app.php?act=pages&id=622&auth_key={auth_key}&viewer_id={user_id}&group_id=182985865&api_id=7055214'

    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    t_res = soup.body.find_all('div', class_='portlet-body')[0]
    res_dict = dict()

    for i in t_res.find_all('li'):
        z = list()
        for j in i.text.split():
            if j.endswith(':'):
                item = ' '.join(i.text.split()[:i.text.split().index(j) + 1])
                z.append(item.replace(':', '').replace('.', ''))
            if j.isdigit():
                z.append(int(j))
                z.append((round((int(j) / 10) ** 0.5 * 10) + 100) / 100)
        res_dict[z[0]] = [z[1], z[2]]
    return res_dict


def _stats(auth_key: str, user_id: int) -> dict:
    url = f"https://vip3.activeusers.ru/app.php?act=user&auth_key={auth_key}&viewer_id={user_id}&group_id=182985865&api_id=7055214"

    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    stat = []
    for i in soup.body.find_all('span', class_='money-list-rescount'):
        stat.append(int(i.text.replace(u'\xa0', '')))
    res = {'level': stat[0], 'attack': stat[1], 'defence': stat[2],
           'strength': stat[3], 'agility': stat[4], 'endurance': stat[5],
           'luck': stat[6], 'accuracy': stat[7], 'concentration': stat[8]}
    return res


def _inv(auth_key: str, user_id: int):
    url = f"https://vip3.activeusers.ru/app.php?act=user&auth_key={auth_key}&viewer_id={user_id}&group_id=182985865&api_id=7055214"

    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    t1 = soup.body.find_all('div', class_='resitems items clearfix')[2]
    return [int(i['class'][1][1:]) for i in t1.find_all('a')]


def get_profile(auth: str, id_vk: int) -> dict:
    res = dict()
    res['items'] = _inv(auth, id_vk)
    res['stats'] = _stats(auth, id_vk)
    return res


def get_books(item_list: list) -> list:
    __BOOK_LIST = items.equipped_to_ordinary_active.copy()
    __BOOK_LIST.update(items.equipped_to_ordinary_passive.copy())
    __ADM_DICT = items.adm_to_ordinary_books.copy()
    res = list()
    for item in item_list:
        if item in __BOOK_LIST.keys():
            res.append(__BOOK_LIST[item])
        if item in __ADM_DICT.keys():
            res += __ADM_DICT[item]
    return res


def get_build(item_list: list) -> dict:
    __BOOK_LIST = items.equipped_books_active + items.equipped_books_passive
    __ADM_DICT = items.adm_to_equipped_books
    __WEAPON_DICT = items.adm_weapons_to_equipped_books
    __WEAPON_DICT.update(items.ordinary_weapons_to_equipped_books)
    res = {'books': [], 'adms': [], 'weapons': []}
    for item in item_list:
        if item in __BOOK_LIST:
            res['books'].append(item)
        if item in __ADM_DICT.keys():
            res['adms'] += __ADM_DICT[item]
        if item in __WEAPON_DICT.keys():
            res['weapons'] += __WEAPON_DICT[item]
    return res


def get_buff_class(auth_key: str, user_id: int) -> int:
    for val in _inv(auth_key, user_id):
        if val in [14088, 14093, 14256, 14257, 14264]:  # class ids
            return val
    return None


def get_races(auth_key: str, user_id: int) -> List[int]:
    return [val for val in _inv(auth_key, user_id) if val in items.races]


def get_voices(auth_key: str, user_id: int) -> int:
    url = f"https://vip3.activeusers.ru/app.php?act=item&id=14264&auth_key={auth_key}&viewer_id={user_id}&group_id=182985865&api_id=7055214"

    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    voices = soup.find_all('h4')[0].text
    import re
    return int(re.findall(r'\d+(?=/\d+)', voices)[0])


def price(item: int) -> int:
    url = f'https://vip3.activeusers.ru/app.php?act=item&id={item}&auth_key=5153d58b92d71bda47f1dac05afc187a&viewer_id=158154503&group_id=182985865&api_id=7055214'

    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    try:
        t1 = soup.body
        try:
            t2 = t1.find_all('div', class_='portlet')[1]
            t3 = t2.find_all('script')[0]
            t4 = str(t3)[str(t3).find('window.graph_data'):]
            t5 = json.loads(t4[20:t4.find(';')])
            return round(sum([i[1] for i in t5]) / len(t5))
        except IndexError:
            return -1
    except TypeError:
        return -1


def sellable_items():
    url = 'https://vip3.activeusers.ru/app.php?act=user&auth_key=5153d58b92d71bda47f1dac05afc187a&viewer_id=158154503&group_id=182985865&api_id=7055214'
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    t1 = soup.find_all('li', class_='dropdown-submenu')
    sellable = [t1[1], t1[2], t1[3], t1[4], t1[5], t1[7], t1[8], t1[9], t1[10]]
    res = []
    for t in sellable:
        for i in t.find_all('li'):
            if i.span.text.startswith(' +'):
                data = i.a['href']
                res.append(int(data[data.find('&id=') + 4:data.find('&auth_key=')]))
    return res


def ingredients():
    url = 'https://vip3.activeusers.ru/app.php?act=user&auth_key=5153d58b92d71bda47f1dac05afc187a&viewer_id=158154503&group_id=182985865&api_id=7055214'
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    t1 = soup.find_all('li', class_='dropdown-submenu')
    sellable = [t1[0]]
    res = []
    for t in sellable:
        for i in t.find_all('li'):
            data = i.a['href']
            res.append(int(data[data.find('&id=') + 4:data.find('&auth_key=')]))
    return res


def header(param: int = 0):

    url = 'https://vip3.activeusers.ru/app.php?act=user&auth_key=5153d58b92d71bda47f1dac05afc187a&viewer_id=158154503&group_id=182985865&api_id=7055214'
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    t1 = soup.find_all('li', class_='dropdown-submenu')
    if 0 <= param < 17 and param != 13:
        sellable = [t1[param]]
    else:
        sellable = [*t1[:13], *t1[14:17]]

    res = {}
    for t in sellable:
        for i in t.find_all('li'):
            data = i.a['href']
            if 'act=item' in data:
                res[int(data[data.find('&id=') + 4:data.find('&auth_key=')])] = i.span.text.strip()
    return res


if __name__ == '__main__':
    # upd_items(12000, 15000)
    pass
