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
from market_data.data import InvalidTickerError

class MarketDataTests(unittest.TestCase):

    def test_app_not_initialised_before_use_raises_error(self):
        app = MarketData()

        with self.assertRaises(NotInitialisedError):
            app.add_security('AMZN')
            sec_list = app.get_securities_list()

    # NOTE(steve): Testing two functions instead of each 
    # individually as individual tests will require
    # knowledge of the implementation.
    def test_add_and_get_securities_list(self):
        app = MarketData()
        app.run()

        app.add_security('AMZN')
        actual_sec_list = app.get_securities_list()
        self.assertEqual(actual_sec_list, ['AMZN'])

        app.add_security('GOOG')
        actual_sec_list = app.get_securities_list()
        self.assertEqual(actual_sec_list, ['AMZN', 'GOOG'])

        app.close()

    def test_not_initialised_error_after_app_close(self):
        app = MarketData()
        app.run()
        app.add_security('AMZN')
        app.close()

        with self.assertRaises(NotInitialisedError):
            app.add_security('GOOG')

class EquityDataTests(unittest.TestCase):

    def test_ticker_not_in_list(self):
        app = MarketData()
        app.run()

        # AMZN is a valid ticker
        with self.assertRaises(InvalidTickerError):
            app.get_equity_data('AMZN', datetime.datetime(2019, 8, 27))

    @patch('market_data.scraper.Scraper.scrape_equity_data', autospec=True)
    def test_invalid_ticker_in_get_equity_data(self, mock_scraper):
        app = MarketData()
        app.run()
        app.add_security('AMZNN')

        mock_scraper.side_effect = InvalidTickerError
        with self.assertRaises(InvalidTickerError):
            app.get_equity_data('AMZNN', datetime.datetime(2019, 8, 27))

    def test_invalid_date_in_get_equity_data(self):
        self.fail('Not implemented')

    @patch('market_data.scraper.Scraper.scrape_equity_data', autospec=True)
    def test_get_equity_data(self, mock_scraper):
        app = MarketData()
        app.run()
        app.add_security('AMZN')

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

        data = app.get_equity_data('AMZN', datetime.datetime(2019, 5, 10))
        self.assertEqual(data, expected_data)

        app.close()

if __name__ == '__main__':
    unittest.main()
