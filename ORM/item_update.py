from ORM import session, Item

import os, json

import config


def load_items():
    f = json.loads(open(os.environ['ITEM_FILE']).read())
    with session() as db:
        for item in f:
            search: Item = db.query(Item).filter(Item.item_id == int(item)).first()
            if search:
                search.item_name = f[item]['name']
                search.item_has_price = bool(f[item]['sell'])
            else:
                search = Item(int(item), f[item]['name'], bool(f[item]['sell']))
            db.add(search)
        db.commit()


if __name__ == '__main__':
    load_items()
