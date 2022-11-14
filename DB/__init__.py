import mariadb as sql
from config import db_data


class DB(object):
    """
    Object of connection to DB. Have single instance for avoid multiple connections
    """
    try:
        _connection = sql.connect(user=db_data['user'], password=db_data['password'],
                                  host='host.docker.internal', database=db_data['database'])
    except:
        _connection = sql.connect(user=db_data['user'], password=db_data['password'],
                                  host=db_data['host'], database=db_data['database'])

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            orig = super(DB, cls)
            cls._instance = orig.__new__(cls)
        return cls._instance

    def connect(self):
        try:
            self._connection = sql.connect(user=db_data['user'], password=db_data['password'],
                                           host='host.docker.internal', database=db_data['database'])
        except:
            self._connection = sql.connect(user=db_data['user'], password=db_data['password'],
                                           host=db_data['host'], database=db_data['database'])

        return self._connection

    def query(self, query_str: str, data: tuple = None) -> (tuple, None):
        db = self.connect()
        cur = db.cursor()
        res = None

        try:
            cur.execute(query_str, data)
            try:
                res = cur.fetchall()
            except sql.ProgrammingError:
                pass
            db.commit()
        except sql.ProgrammingError as exc:
            db.rollback()
            raise KeyError(exc)
        except sql.IntegrityError:
            db.rollback()
        finally:
            cur.close()
            db.close()
        return res


if __name__ == '__main__':
    item = 'Рассечение'
    query = "SELECT * FROM items WHERE item_name LIKE CONCAT('Книга - ', %s, '%');"
    print(DB().query(query, (item,)))
