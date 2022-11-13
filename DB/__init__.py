import mysql.connector as sql
from config import db_data

import mysql.connector.errors as sql_err


class DB(object):
    """
    Object of connection to DB. Have single instance for avoid multiple connections
    """
    try:
        _connection = sql.connect(user=db_data['user'], password=db_data['password'],
                                  host='host.docker.internal', database=db_data['database'], port=3305)
    except:
        _connection = sql.connect(user=db_data['user'], password=db_data['password'],
                                  host=db_data['host'], database=db_data['database'], port=3305)

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            orig = super(DB, cls)
            cls._instance = orig.__new__(cls)
        return cls._instance

    def connect(self):
        if not self._connection.is_connected():
            try:
                self._connection = sql.connect(user=db_data['user'], password=db_data['password'],
                                               host='host.docker.internal', database=db_data['database'], port=3305)
            except:
                self._connection = sql.connect(user=db_data['user'], password=db_data['password'],
                                               host=db_data['host'], database=db_data['database'], port=3305)

        return self._connection

    def query(self, query_str: str, data: tuple = None) -> (tuple, None):
        db = self.connect()
        cur = db.cursor()
        res = None

        try:
            cur.execute(query_str, data)
            res = cur.fetchall()
            db.commit()
        except sql_err.ProgrammingError as exc:
            db.rollback()
            raise KeyError(exc.msg)
        except sql_err.IntegrityError:
            db.rollback()
        finally:
            cur.close()
            db.close()
        return res


if __name__ == '__main__':
    item = 'Рассечение'
    query = "SELECT * FROM items WHERE item_name LIKE CONCAT('Книга - ', %s, '%');"
    print(DB().query(query, (item,)))
