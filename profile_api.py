from bs4 import BeautifulSoup
import requests
import json

from typing import List, Union, Dict

from dictionaries import items

from logger import get_logger

logger = get_logger(__name__, 'profile_requests')

# TODO: Refactor for urllib
def get_name(item_id: int) -> str:
    url = f'https://vip3.activeusers.ru/app.php?act=item&id={item_id}&auth_key=5153d58b92d71bda47f1dac05afc187a&viewer_id=158154503&group_id=182985865&api_id=7055214'
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    try:
        return soup.find_all('div', class_='shop_res-title')[0].contents[0].strip()
    except:
        return ''


def lvl_active(auth_key: str, user_id: int) -> Dict[str, List[Union[int, float]]]:
    url = f'https://vip3.activeusers.ru/app.php?act=pages&id=620&auth_key={auth_key}&viewer_id={user_id}&group_id=182985865&api_id=7055214'
    logger.info(f"[GET] Request to {url}")

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
    logger.info(f"[GET] Request to {url}")

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

    logger.info(f"[GET] Request to {url}")

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

    logger.info(f"[GET] Request to {url}")

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
    __ADM_DICT = items.adm_to_equipped_books
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
    res = {'books': [], 'adms': []}
    for item in item_list:
        if item in __BOOK_LIST:
            res['books'].append(item)
        if item in __ADM_DICT.keys():
            res['adms'] += __ADM_DICT[item]
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

    logger.info(f"[GET] Request to {url}")

    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    voices = soup.find_all('h4')[0].text
    import re
    return int(re.findall(r'\d+(?=/\d+)', voices)[0])


def price(item: int) -> int:
    url = f'https://vip3.activeusers.ru/app.php?act=item&id={item}&auth_key=5153d58b92d71bda47f1dac05afc187a&viewer_id=158154503&group_id=182985865&api_id=7055214'
    logger.info(f"[GET] Request to {url}")

    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    try:
        t1 = soup.body
        try:
            t2 = t1.find_all('div', class_='portlet')[1]
            t3 = t2.find_all('script')[1]
            t4 = str(t3)[str(t3).find('window.graph_data'):]
            t5 = json.loads(t4[20:t4.find(';')])
            return round(sum([i[1] for i in t5]) / len(t5))
        except IndexError:
            return -1
    except TypeError:
        return -1


def upd_items(start_id=12000, stop_id=20000):

    import time
    import json

    items = json.loads(open('items.json', 'r').read())

    for i in range(start_id, stop_id):
        time.sleep(0.1)
        n = get_name(i)
        if n != '':
            print('\n', i, ': ', n, sep='', end=' ')
            if price(i) > 0:
                items[i] = {'name': n, 'sell': 1}
            else:
                items[i] = {'name': n, 'sell': 0}
        else:
            print(i, end=' ')

    open('items.json', 'w').write(json.dumps(items))

    return


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
    upd_items(12000, 15000)
