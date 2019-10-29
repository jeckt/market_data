from collections import namedtuple
import json

from market_data.scraper import Scraper
from market_data.data import InvalidTickerError, InvalidDateError, NoDataError
from market_data.data_adapter import DatabaseNotFoundError
import market_data.data_adapter as data_adapter

class MarketData:

    Database = namedtuple('Database', ['conn_string', 'source'])
    _init = False


    # NOTE(steve): this method will be used to initialise all 
    # the dependencies before the user can use the application
    # this is where we will throw dependency errors as well
    # TODO(steve): the DataAdapter should be passed into the 
    # MarketData class not a connection string to connect to
    # the database???
    def run(self, database):
        """
        Initialises MarketData class with scraper and data adapter.

        Args:
            database: namedtuple('Database', ['conn_string', 'source']).
        """
        self._init = True
        self._scraper = Scraper('yahoo')
        da = data_adapter.get_adapter(database.source)
        self._database = da.connect(database.conn_string)

    # NOTE(steve): this method will be used to clean up
    # all the dependency e.g. closing of the database
    # after the app is closed
    def close(self):
        """Ensures dependent objects are properly cleaned up."""
        self._init = False
        self._database.close()

    # TODO(steve): should turn this into a decorator
    def _check_initialised(self):
        """Checks if class is initialised."""
        if not self._init:
            raise NotInitialisedError('Call run method first!')

    def add_security(self, ticker):
        """
        Add security into market data.

        Args:
            ticker: Yahoo ticker for the security to be added.
        """
        self._check_initialised()
        self._database.insert_securities([ticker])

    def get_securities_list(self):
        """
        Returns list of securities currently stored.

        Returns:
            List of security tickers.
        """
        self._check_initialised()
        return self._database.get_securities_list()

    def get_equity_data(self, ticker, dt):
        """
        Returns equity data object (open, high, low, close, adj_close, volume)
        for a selected ticker (Yahoo) and date.

        Args:
            ticker: Yahoo ticker.
            dt: date of equity data.

        Returns:
            Equity data object (open, high, low, close, adj_close, volume)
            for the selected ticker and date if available.

        Raises:
            InvalidTickerError: Security not in market data.
            InvalidDateError: No equity data for date provided.
        """
        self._check_initialised()
        data = self._database.get_equity_data(ticker, dt)
        return data

    def get_equity_data_series(self, ticker):
        """
        Return equity data for all available dates for the selected ticker.

        Args:
            ticker: Yahoo ticker.

        Returns:
            Equity data series sorted by date (newest to oldest) as a list of
            tuples (date, equity_data).

        Raises:
            InvalidTickerError: Security not in market data.
        """
        self._check_initialised()
        data = self._database.get_equity_data_series(ticker)
        return data

    def get_latest_equity_data(self, ticker):
        """
        Return the most recent equity data object for the selected ticker.

        Args:
            ticker: Yahoo ticker.

        Returns:
            Most recent equity data object by date (open, high, low, close,
            adj_close, volume) for the selected ticker.

        Raises:
            InvalidTickerError: Security not in market data.
            NoDataError: No data availabe for selected security.
        """
        self._check_initialised()
        data = self.get_equity_data_series(ticker)
        if len(data) > 0:
            return data[0]
        else:
            raise NoDataError(ticker)

    def update_market_data(self, ticker, dt):
        """
        Updates market data for the selected security and date.

        Args:
            ticker: Yahoo ticker.
            dt: date of equity data.

        Raise:
            InvalidTickerError: Security not in market data.
        """
        self._check_initialised()
        if ticker in self._database.get_securities_list():
            data = self._scraper.scrape_equity_data(ticker, dt)
            self._database.update_market_data(ticker, (dt, data))
        else:
            raise InvalidTickerError(ticker)

class NotInitialisedError(Exception):
    pass
