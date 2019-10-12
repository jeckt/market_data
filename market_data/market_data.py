from collections import namedtuple
import json
from market_data.scraper import Scraper
from market_data.data import InvalidTickerError, InvalidDateError, NoDataError
from market_data.data_adapter import DatabaseNotFoundError
import market_data.data_adapter as data_adapter

class MarketData:

    Database = namedtuple('Database', ['conn_string', 'source'])
    init = False


    # NOTE(steve): this method will be used to initialise all 
    # the dependencies before the user can use the application
    # this is where we will throw dependency errors as well
    # TODO(steve): the DataAdapter should be passed into the 
    # MarketData class not a connection string to connect to
    # the database???
    # NOTE(steve): database param is a named tuple
    # Database = namedtuple('Database', ['conn_string', 'source'])
    def run(self, database):
        self.init = True
        self._scraper = Scraper('yahoo')
        da = data_adapter.get_adapter(database.source)
        self._database = da.connect(database.conn_string)

    # NOTE(steve): this method will be used to clean up
    # all the dependency e.g. closing of the database
    # after the app is closed
    def close(self):
        self.init = False
        self._database.close()

    # TODO(steve): should turn this into a decorator
    def _check_initialised(self):
        if not self.init:
            raise NotInitialisedError('Call run method first!')

    def add_security(self, ticker):
        self._check_initialised()
        self._database.insert_securities([ticker])

    def get_securities_list(self):
        self._check_initialised()
        return self._database.get_securities_list()

    def get_equity_data(self, ticker, dt):
        self._check_initialised()
        data = self._database.get_equity_data(ticker, dt)
        return data

    def get_equity_data_series(self, ticker):
        self._check_initialised()
        data = self._database.get_equity_data_series(ticker)
        return data

    def get_latest_equity_data(self, ticker):
        self._check_initialised()
        data = self.get_equity_data_series(ticker)
        if len(data) > 0:
            return data[0]
        else:
            raise NoDataError(ticker)

    def update_market_data(self, ticker, dt):
        self._check_initialised()
        if ticker in self._database.get_securities_list():
            data = self._scraper.scrape_equity_data(ticker, dt)
            self._database.update_market_data(ticker, (dt, data))
        else:
            raise InvalidTickerError(ticker)

class NotInitialisedError(Exception):
    pass
