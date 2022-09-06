import mysql.connector as sql
from config import db_data


class DB(object):
    """
    Object of connection to DB. Have single instance for avoid multiple connections
    """
    _connection = sql.connect(user=db_data['user'], password=db_data['password'],
                              host=db_data['host'], database=db_data['database'])

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            orig = super(DB, cls)
            cls._instance = orig.__new__(cls)
        return cls._instance

    def connect(self):
        if not self._connection.is_connected():
            self._connection = sql.connect(user=db_data['user'], password=db_data['password'],
                                           host=db_data['host'], database=db_data['database'])
        return self._connection
