from bs4 import BeautifulSoup
import requests
import json


# TODO: Add using for this
from typing import List, Union, Dict


def _id_tag(tag, search, skip=0) -> int:
    for j in range(len(tag.find_all('div'))):
        if search in tag.find_all('div')[j]['class']:
            if skip > 0:
                skip -= 1
            else:
                return j


def get_name(item_id: int) -> str:
    url = f'https://vip3.activeusers.ru/app.php?act=item&id={item_id}&auth_key=5153d58b92d71bda47f1dac05afc187a&viewer_id=158154503&group_id=182985865&api_id=7055214'
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    t1 = soup.body
    t2 = t1.find_all('div')[_id_tag(t1, 'app_item')].div.div.div.div
    try:
        t3 = t2.find_all('div')[_id_tag(t2, 'shop_res-title')]
        return t3.contents[0].strip()
    except:
        return ''


def _active(auth_key: str, user_id: int) -> List[List[Union[str, int, float]]]:
    url = f'https://vip3.activeusers.ru/app.php?act=pages&id=620&auth_key={auth_key}&viewer_id={user_id}&group_id=182985865&api_id=7055214'
    print(f"[GET] Request to {url}")

    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    t1 = soup.body
    t2 = t1.find_all('div')[_id_tag(t1, 'app_pages')]
    t3 = t2.div.div.div.div
    res_list = list()

    for i in t3.find_all('li'):
        z = list()
        for j in i.text.split():
            if j.endswith(':'):
                z.append(' '.join(i.text.split()[:i.text.split().index(j) + 1]))
            if j.isdigit():
                z.append(int(j))
                z.append((round((int(j) / 10) ** 0.5 * 10) + 100) / 100)
        res_list.append(z)
    return res_list


def _passive(auth_key: str, user_id: int) -> List[List[Union[str, int, float]]]:
    url = f'https://vip3.activeusers.ru/app.php?act=pages&id=622&auth_key={auth_key}&viewer_id={user_id}&group_id=182985865&api_id=7055214'
    print(f"[GET] Request to {url}")

    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    t1 = soup.body
    t2 = t1.find_all('div')[_id_tag(t1, 'app_pages')]
    t3 = t2.div.div.div.div
    res_list = list()

    for i in t3.find_all('li'):
        z = list()
        for j in i.text.split():
            if j.endswith(':'):
                z.append(' '.join(i.text.split()[:i.text.split().index(j) + 1]))
            if j.isdigit():
                z.append(int(j))
                z.append((round((int(j) / 10) ** 0.5 * 10) + 100) / 100)
        res_list.append(z)
    return res_list


def _stats(auth_key: str, user_id: int) -> dict:
    url = f"https://vip3.activeusers.ru/app.php?act=user&auth_key={auth_key}&viewer_id={user_id}&group_id=182985865&api_id=7055214"

    print(f"[GET] Request to {url}")

    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    t1 = soup.body
    t2 = t1.find_all('div')[_id_tag(t1, 'profile-content')]
    t3 = t2.div.div.div.div
    t4 = t3.find_all('div')[_id_tag(t3, 'portlet-body')]
    t5 = t4.find_all('span')
    stat = []
    for i in range(0, len(t5), 2):
        stat.append(int(t5[i].text.replace(u'\xa0', '')))
    res = {'level': stat[0], 'attack': stat[1], 'defence': stat[2],
           'strength': stat[3], 'agility': stat[4], 'endurance': stat[5],
           'luck': stat[6], 'accuracy': stat[7], 'concentration': stat[8]}
    return res


def _inv(auth_key: str, user_id: int):
    url = f"https://vip3.activeusers.ru/app.php?act=user&auth_key={auth_key}&viewer_id={user_id}&group_id=182985865&api_id=7055214"

    print(f"[GET] Request to {url}")

    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    t1 = soup.body
    t2 = t1.find_all('div')[_id_tag(t1, 'app_user')]
    t3 = t2.div.div
    t4 = t3.find_all('div')[_id_tag(t3, 'progress-box')]
    t5 = t4.find_all('div')[2].div
    res_list = list()
    for i in t5.find_all('a'):
        res_list.append(int(i['href'][i['href'].find('id=') + 3:i['href'].find('id=') + 8]))
    return res_list


def get_profile(auth: str, id_vk: int) -> dict:
    res = dict()
    res['items'] = _inv(auth, id_vk)
    res['stats'] = _stats(auth, id_vk)
    return res


def get_books(item_list: list) -> list:
    BOOK_LIST = {
        13408: 13580, 13409: 13581, 13547: 13582, 13553: 13583, 13586: 13592, 13593: 13595, 13598: 13600, 13601: 13603,
        13604: 13606, 13607: 13609, 13610: 13612, 13613: 13615, 13616: 13619, 13621: 13623, 13625: 13626, 13627: 13628,
        13638: 13639, 13641: 13642, 13643: 13644, 13645: 13646, 13647: 13648, 13649: 13650, 13651: 13652, 13653: 13654,
        13655: 13656, 13657: 13658, 13659: 13660, 13661: 13662, 13663: 13664, 13665: 13666, 13667: 13668, 13669: 13670,
        13671: 13672, 13673: 13674, 13676: 13677, 13678: 13679, 13680: 13681, 13682: 13683, 13684: 13685, 13686: 13687,
        13688: 13689, 13690: 13691, 13692: 13693, 13694: 13695, 13696: 13697, 13698: 13699, 14506: 14505, 14508: 14507,
        14778: 14777, 14780: 14779, 14971: 14970, 14973: 14972, 14987: 14986, 14989: 14988, 15220: 15219
    }
    ADM_DICT = {
        14128: [13652], 14130: [13646], 14132: [13660], 14134: [13642, 13639], 14136: [13668], 14138: [13683],
        14140: [13644], 14142: [13681], 14144: [13650], 14302: [13652, 13646, 13660],
        14304: [13642, 13639, 13668, 13683],
        14306: [13644, 13681, 13650], 14573: [13697], 14575: [13672], 14577: [13693], 14579: [13697, 13672, 13693],
        14869: [13658], 14920: [13685], 15019: [13691], 15021: [13662], 15023: [13664], 15025: [13691, 13662, 13664]
    }
    res = list()
    for item in item_list:
        if item in BOOK_LIST.keys():
            res.append(BOOK_LIST[item])
        if item in ADM_DICT.keys():
            res += ADM_DICT[item]
    return res


def get_build(item_list: list) -> dict:
    BOOK_LIST = [13408, 13409, 13547, 13553, 13586, 13593, 13598, 13601, 13604, 13607, 13610, 13613, 13616, 13621,
                 13625, 13627, 13638, 13641, 13643, 13645, 13647, 13649, 13651, 13653, 13655, 13657, 13659, 13661,
                 13663, 13665, 13667, 13669, 13671, 13673, 13676, 13678, 13680, 13682, 13684, 13686, 13688, 13690,
                 13692, 13694, 13696, 13698, 14506, 14508, 14778, 14780, 14971, 14973, 14987, 14989, 15220]
    ADM_DICT = {
        14128: [13651], 14130: [13645], 14132: [13659], 14134: [13641, 13638], 14136: [13667], 14138: [13682],
        14140: [13643], 14142: [13680], 14144: [13649], 14302: [13651, 13645, 13659], 14304: [13641, 13638, 13667, 13682],
        14306: [13643, 13680, 13649], 14573: [13696], 14575: [13671], 14577: [13692], 14579: [13696, 13671, 13692],
        14869: [13657], 14920: [13684], 15019: [13690], 15021: [13661], 15023: [13663], 15025: [13690, 13661, 13663]
    }
    res = {'books': [], 'adms': []}
    for item in item_list:
        if item in BOOK_LIST:
            res['books'].append(item)
        if item in ADM_DICT.keys():
            res['adms'] += ADM_DICT[item]
    return res


def price(item: int) -> int:
    url = f'https://vip3.activeusers.ru/app.php?act=item&id={item}&auth_key=5153d58b92d71bda47f1dac05afc187a&viewer_id=158154503&group_id=182985865&api_id=7055214'
    print(f"[GET] Request to {url}")

    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    try:
        t1 = soup.body
        t2 = t1.find_all('div')[_id_tag(t1, 'app_item')]
        t3 = t2.div.div
        t4 = t3.find_all('div')[_id_tag(t3, 'section')]
        t5 = t4.find_all('div')[_id_tag(t4, 'portlet')]
        t6 = t5.find_all('div')[_id_tag(t5, 'row', 1)]
        t7 = t6.div.div.div.find_all('script')[1]
        t8 = str(t7)[str(t7).find('window.graph_data'):]
        t9 = json.loads(t8[20:t8.find(';')])
        price_list = list()
        for i in t9:
            price_list.append(i[1])
        return round(sum(price_list) / 20)
    except TypeError:
        return -1


def upd_items():

    import time
    import json

    items = json.loads(open('items.json', 'r').read())

    for i in range(15000, 20000):
        time.sleep(0.1)
        n = get_name(i)
        if n != '':
            print('\n', i, ': ', n, sep='', end=' ')
            items[i] = n
        else:
            print(i, end=' ')

    open('items.json', 'w').write(json.dumps(items))

    return


if __name__ == '__main__':
    upd_items()
