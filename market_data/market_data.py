import json
from market_data.scraper import Scraper
from market_data.data import InvalidTickerError, InvalidDateError
from market_data.data_adapter import DatabaseNotFoundError
from market_data.data_adapter import DataAdapter

class MarketData:

    init = False

    # NOTE(steve): this method will be used to initialise all 
    # the dependencies before the user can use the application
    # this is where we will throw dependency errors as well
    # TODO(steve): the DataAdapter should be passed into the 
    # MarketData class not a connection string to connect to
    # the database
    def run(self, database=None):
        self.init = True
        self._scraper = Scraper('yahoo')
        self._database = DataAdapter.connect(database)

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

    def update_market_data(self, ticker, dt):
        self._check_initialised()
        if ticker in self._database.get_securities_list():
            data = self._scraper.scrape_equity_data(ticker, dt)
            self._database.update_market_data(ticker, (dt, data))
        else:
            raise InvalidTickerError(ticker)

class NotInitialisedError(Exception):
    pass
