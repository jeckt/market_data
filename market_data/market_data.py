import json
from market_data.scraper import Scraper
from market_data.data import InvalidTickerError
from market_data.data_adapter import DatabaseNotFoundError
from market_data.data_adapter import DataAdapter

class MarketData:

    init = False

    # NOTE(steve): this method will be used to initialise all 
    # the dependencies before the user can use the application
    # this is where we will throw dependency errors as well
    def run(self, database=None):
        self.init = True
        self._scraper = Scraper('yahoo')
        self._database = DataAdapter.connect(database)

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
        if ticker in self._database.get_securities_list():
            data = self._scraper.scrape_equity_data(ticker, dt)
        else:
            raise InvalidTickerError("ticker")

        return data

    # NOTE(steve): this method will be used to clean up
    # all the dependency e.g. closing of the database
    # after the app is closed
    def close(self):
        self.init = False
        self._database.close()

class NotInitialisedError(Exception):
    pass
