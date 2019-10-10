import os
import sqlite3
import market_data.data_adapter as data_adapter
from market_data.data import EquityData, InvalidTickerError, InvalidDateError

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
            with conn:
                security_list_sql = """CREATE TABLE securities(
                                        id integer PRIMARY KEY AUTOINCREMENT,
                                        ticker text NOT NULL,
                                        UNIQUE(ticker)
                                        );"""
                cursor = conn.cursor()
                cursor.execute(security_list_sql)

                equity_data_sql = """CREATE TABLE equity_prices(
                                        id integer PRIMARY KEY AUTOINCREMENT,
                                        ticker_id integer NOT NULL,
                                        date text NOT NULL,
                                        open real NOT NULL,
                                        high real NOT NULL,
                                        low real NOT NULL,
                                        close real NOT NULL,
                                        adj_close real NOT NULL,
                                        volume integer NOT NULL,
                                        UNIQUE(ticker_id, date)
                                        FOREIGN KEY(ticker_id)
                                        REFERENCES securities(id)
                                        );"""
                cursor.execute(equity_data_sql)

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
        self._conn = sqlite3.connect(self.conn_string)

    # TODO(steve): should this be a decorator???
    def _check_is_valid_security(self, security):
        tickers = self.get_securities_list()
        if security not in tickers:
            raise InvalidTickerError(security)

    def close(self):
        if self._conn is not None:
            self._conn.close()

    def get_securities_list(self):
        with self._conn:
            cursor = self._conn.cursor()
            cursor.execute('SELECT ticker FROM securities')
            rows = cursor.fetchall()
        return [row[0] for row in rows]

    def insert_securities(self, securities_to_add):
        sql = 'INSERT INTO securities(ticker) VALUES(?)'
        with self._conn:
            cursor = self._conn.cursor()
            for security in securities_to_add:
                try:
                    cursor.execute(sql, (security,))
                except sqlite3.IntegrityError:
                    pass

    def update_market_data(self, security, equity_data):
        self._check_is_valid_security(security)

    def get_equity_data(self, security, dt):
        self._check_is_valid_security(security)

    def get_equity_data_series(self, security):
        self._check_is_valid_security(security)
