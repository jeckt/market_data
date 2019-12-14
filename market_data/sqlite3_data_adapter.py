import os
import datetime
from decimal import Decimal
import sqlite3

import freezegun

import market_data.data_adapter as data_adapter
from market_data.data import EquityData, InvalidTickerError, InvalidDateError

def adapt_date(dt):
    return dt.strftime('%Y-%m-%d')

sqlite3.register_adapter(Decimal, lambda d: str(d))
sqlite3.register_converter("decimal", lambda d: Decimal(d.decode('utf-8')))

# NOTE(steve): freezegun has some pecularities where in certain situations
# it does not use the datetime.datetime adapter to convert datetime objects
# to string for the sqlite3 database so we explicit convert it
sqlite3.register_adapter(freezegun.api.FakeDatetime, adapt_date)
sqlite3.register_adapter(datetime.datetime, adapt_date)
sqlite3.register_converter("date",
        lambda dt: datetime.datetime.strptime(dt.decode('utf-8'), '%Y-%m-%d'))

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
            conn = sqlite3.connect(database,
                                   detect_types=sqlite3.PARSE_DECLTYPES)
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
                                        date date NOT NULL,
                                        open decimal NOT NULL,
                                        high decimal NOT NULL,
                                        low decimal NOT NULL,
                                        close decimal NOT NULL,
                                        adj_close decimal NOT NULL,
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
        self._conn = sqlite3.connect(self.conn_string,
                                    detect_types=sqlite3.PARSE_DECLTYPES)
        self._conn.execute('PRAGMA foreign_keys = ON')

    # TODO(steve): should this be a decorator???
    def _check_is_valid_security(self, security):
        tickers = self.get_securities_list()
        if security not in tickers:
            raise InvalidTickerError(security)

    def _get_security_id(self, security):
        with self._conn:
            sql = "SELECT id FROM securities WHERE ticker = ?"
            cursor = self._conn.cursor()
            cursor.execute(sql, (security,))
            ticker_id = cursor.fetchone()[0]

        return ticker_id

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

        ticker_id = self._get_security_id(security)
        date, data = equity_data[0], equity_data[1]

        with self._conn:
            sql = """REPLACE INTO equity_prices(ticker_id, date, open,
                        high, low, close, adj_close, volume)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
            cursor = self._conn.cursor()
            cursor.execute(sql, (ticker_id, date, data.open, data.high,
                                 data.low, data.close, data.adj_close,
                                 data.volume))

    def bulk_update_market_data(self, security, equity_data):
        self._check_is_valid_security(security)

        ticker_id = self._get_security_id(security)

        # TODO(steve): find a more efficient way to update the database
        # instead of updating rows one by one
        with self._conn:
            for d in equity_data:
                date, data = d[0], d[1]
                sql = """REPLACE INTO equity_prices(ticker_id, date, open,
                            high, low, close, adj_close, volume)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
                cursor = self._conn.cursor()
                cursor.execute(sql, (ticker_id, date, data.open, data.high,
                                     data.low, data.close, data.adj_close,
                                     data.volume))

    def _get_equity_data(self, ticker_id, date):
        with self._conn:
            sql = """SELECT open, high, low, close, adj_close, volume
                        FROM equity_prices WHERE (ticker_id = ? and
                        date = ?)"""
            cursor = self._conn.cursor()
            cursor.execute(sql, (ticker_id, date))

            rows = cursor.fetchall()

        return rows

    def get_equity_data(self, security, date):
        self._check_is_valid_security(security)

        ticker_id = self._get_security_id(security)

        rows = self._get_equity_data(ticker_id, date)
        if len(rows) == 0:
            raise InvalidDateError(date)
        elif len(rows) == 1:
            data = EquityData(*rows[0])
            return data

    def get_equity_data_series(self, security):
        self._check_is_valid_security(security)

        ticker_id = self._get_security_id(security)

        with self._conn:
            sql = """SELECT date, open, high, low, close, adj_close, volume
                        FROM equity_prices WHERE (ticker_id = ?)"""

            cursor = self._conn.cursor()
            cursor.execute(sql, (ticker_id,))
            rows = cursor.fetchall()

            data = [(row[0], EquityData(*row[1:])) for row in rows]

            return sorted(data, reverse=True)
