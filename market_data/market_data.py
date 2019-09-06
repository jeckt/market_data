import os
import json
from market_data.scraper import Scraper
from market_data.data import InvalidTickerError

class MarketData:

    init = False

    # NOTE(steve): this method will be used to initialise all 
    # the dependencies before the user can use the application
    # this is where we will throw dependency errors as well
    def run(self, database=None):
        self.init = True
        self._scraper = Scraper('yahoo')

        if not database:
            database = 'prod_data.txt'
            with open(database, 'w') as db:
                json.dump(list(), db)

        try:
            with open(database, 'r') as db:
                self._securities = json.load(db)
        except FileNotFoundError:
            raise DatabaseNotFoundError(database)

    # TODO(steve): should turn this into a decorator
    def _check_initialised(self):
        if not self.init:
            raise NotInitialisedError('Call run method first!')

    def add_security(self, ticker):
        self._check_initialised()
        self._securities.append(ticker)

    def get_securities_list(self):
        self._check_initialised()
        return list(self._securities)

    def get_equity_data(self, ticker, dt):
        self._check_initialised()
        if ticker in self._securities:
            data = self._scraper.scrape_equity_data(ticker, dt)
        else:
            raise InvalidTickerError("ticker")

        return data

    # NOTE(steve): this method will be used to clean up
    # all the dependency e.g. closing of the database
    # after the app is closed
    def close(self):
        self.init = False

class NotInitialisedError(Exception):
    pass

class DatabaseNotFoundError(Exception):
    pass
