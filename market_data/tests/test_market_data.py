#!/usr/bin/env python

import os
import sys
import inspect
file_path = os.path.dirname(inspect.getfile(inspect.currentframe()))
sys.path.insert(0, os.path.split(os.path.split(file_path)[0])[0])

import unittest
from unittest import skip
from unittest.mock import patch
import datetime
from decimal import Decimal

from market_data.market_data import MarketData
from market_data.market_data import NotInitialisedError
from market_data.data import EquityData
from market_data.data import InvalidTickerError, InvalidDateError
from market_data.data_adapter import DataAdapter, DatabaseNotFoundError

class MarketDataTests(unittest.TestCase):

    def setUp(self):
        self.database = DataAdapter.test_database
        DataAdapter.create_test_database()
        self.app = MarketData()
        self.app.run(database=self.database)

    def tearDown(self):
        self.app.close()
        try:
            DataAdapter.delete_test_database()
        except:
            pass

    def test_app_not_initialised_before_use_raises_error(self):
        app = MarketData()

        with self.assertRaises(NotInitialisedError):
            app.add_security('AMZN')
            sec_list = app.get_securities_list()

    # NOTE(steve): Testing two functions instead of each 
    # individually as individual tests will require
    # knowledge of the implementation.
    def test_add_and_get_securities_list(self):
        self.app.add_security('AMZN')
        actual_sec_list = self.app.get_securities_list()
        self.assertEqual(actual_sec_list, ['AMZN'])

        self.app.add_security('GOOG')
        actual_sec_list = set(self.app.get_securities_list())
        self.assertEqual(actual_sec_list, set(['AMZN', 'GOOG']))

    def test_not_initialised_error_after_app_close(self):
        self.app.add_security('AMZN')
        self.app.close()

        with self.assertRaises(NotInitialisedError):
            self.app.add_security('GOOG')

class MarketDataPersistentStorageTests(unittest.TestCase):

    def setUp(self):
        self.database = DataAdapter.test_database
        DataAdapter.create_test_database()

    def tearDown(self):
        try:
            DataAdapter.delete_test_database()
        except:
            pass

    def test_added_security_is_in_list_on_reopen(self):
        app = MarketData()
        app.run(database=self.database)
        ticker = 'TLS'
        app.add_security(ticker)
        app.close()

        new_app = MarketData()
        new_app.run(database=self.database)
        tickers = new_app.get_securities_list()
        new_app.close()
        self.assertEqual([ticker], tickers)

    def test_create_production_database_by_default(self):
        app = MarketData()
        app.run(database=self.database)
        self.assertEqual([], app.get_securities_list())
        app.close()

    def test_raise_database_not_found_error(self):
        app = MarketData()
        with self.assertRaises(DatabaseNotFoundError):
            app.run(database='db.txt')

class EquityDataTests(unittest.TestCase):

    def setUp(self):
        self.database = DataAdapter.test_database
        DataAdapter.create_test_database()
        self.app = MarketData()
        self.app.run(database=self.database)

    def tearDown(self):
        self.app.close()
        try:
            DataAdapter.delete_test_database()
        except:
            pass

    def test_ticker_not_in_list(self):
        # NOTE(steve): AMZN is a valid stock ticker but is not in the list
        with self.assertRaises(InvalidTickerError):
            self.app.get_equity_data('AMZN', datetime.datetime(2019, 8, 27))

    @patch('market_data.scraper.Scraper.scrape_equity_data', autospec=True)
    def test_invalid_ticker_in_get_equity_data(self, mock_scraper):
        self.app.add_security('AMZNN')

        mock_scraper.side_effect = InvalidTickerError
        with self.assertRaises(InvalidTickerError):
            self.app.get_equity_data('AMZNN', datetime.datetime(2019, 8, 27))

    @patch('market_data.scraper.Scraper.scrape_equity_data', autospec=True)
    def test_invalid_date_in_get_equity_data(self, mock_scraper):
        self.app.add_security('AMZN')

        mock_scraper.side_effect = InvalidDateError
        with self.assertRaises(InvalidDateError):
            self.app.get_equity_data('AMZN', datetime.datetime(2017, 8, 25))

    @patch('market_data.scraper.Scraper.scrape_equity_data', autospec=True)
    def test_get_equity_data(self, mock_scraper):
        self.app.add_security('AMZN')

        # NOTE(steve): it is not market data module's responsibility to
        # ensure the scrape equity data function works.
        # It should assume that it returns the correct results
        data = EquityData()
        data.open = Decimal('1898.00')
        data.high = Decimal('1903.79')
        data.low = Decimal('1856.00')
        data.close = Decimal('1889.98')
        data.adj_close = Decimal('1889.98')
        data.volume = int(5718000)

        mock_scraper.return_value = data

        expected_data = EquityData()
        expected_data.open = Decimal('1898.00')
        expected_data.high = Decimal('1903.79')
        expected_data.low = Decimal('1856.00')
        expected_data.close = Decimal('1889.98')
        expected_data.adj_close = Decimal('1889.98')
        expected_data.volume = int(5718000)

        data = self.app.get_equity_data('AMZN', datetime.datetime(2019, 5, 10))
        self.assertEqual(data, expected_data)

if __name__ == '__main__':
    unittest.main()
