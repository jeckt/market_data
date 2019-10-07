import os
import sqlite3
import market_data.data_adapter as data_adapter

class Sqlite3DataAdapter(data_adapter.DataAdapter):
    test_database = 'test.db'

    @classmethod
    def create_test_database(cls):
        cls.create_database(cls.test_database)

    @classmethod
    def delete_test_database(cls):
        if os.path.isfile(cls.test_database):
            os.remove(cls.test_database)
        else:
            raise data_adapter.DatabaseNotFoundError

    @classmethod
    def create_database(cls, database):
        if os.path.isfile(database):
            raise data_adapter.DatabaseExistsError(database)

        try:
            conn = sqlite3.connect(cls.test_database)
        except sqlite3.Error as e:
            print(e)
        finally:
            if conn is not None:
                conn.close()

    @classmethod
    def connect(cls, conn_string):
        if not os.path.isfile(conn_string):
            raise data_adapter.DatabaseNotFoundError

        return cls(conn_string)

    def __init__(self, conn_string):
        self.conn_string = conn_string

    def close(self):
        pass

    def get_securities_list(self):
        pass

    def insert_securities(self, securities_to_add):
        pass

    def update_market_data(self, security, equity_data):
        pass

    def get_equity_data(self, security, dt):
        pass

    def get_equity_data_series(self, security):
        pass
