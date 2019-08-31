#!/usr/bin/env python

import unittest
from unittest import skip
from unittest.mock import patch
import datetime
from decimal import Decimal

from scraper import Scraper, EquityData
from scraper import InvalidSourceError, InvalidTickerError

import os
import inspect
os.chdir((os.path.dirname(inspect.getfile(inspect.currentframe()))))

class ScraperTests(unittest.TestCase):

    def test_scrape_from_valid_source(self):
        scraper = Scraper('yahoo')
        self.assertIsInstance(scraper, Scraper)
        self.assertEqual(scraper.source, 'yahoo')

    def test_invalid_source_scrape_error(self):
        with self.assertRaises(InvalidSourceError):
            scraper = Scraper('google')

class ScraperYahooEquityPricesTests(unittest.TestCase):

    def load_test_data(self):
        test_file = 'amzn_scrape_test_data.html'
        with open(test_file, 'rb') as f:
            data = f.read()

        return data

    @patch('urllib.request.urlopen', autospec=True)
    def test_scrape_returns_correct_equity_data(self, mock_urlopen):
        ticker = 'AMZN'
        dt = datetime.datetime(2019, 8, 23)
        scraper = Scraper('yahoo')

        mock_urlopen_context = mock_urlopen.return_value.__enter__
        mock_urlopen_context.return_value.status = 200
        mock_urlopen_context.read.return_value = self.load_test_data()

        results = scraper.scrape_equity_data(ticker, dt)
        expected_output = EquityData()
        expected_output.open = 1793.03
        expected_output.high = 1804.90
        expected_output.low = 1745.23
        expected_output.close = 1749.62
        expected_output.adj_close = 1749.62
        expected_output.volume = 5270800

        self.assertIsInstance(results, EquityData)
        self.assertEqual(results, expected_output)

    @patch('urllib.request.urlopen', autospec=True)
    def test_scrape_invalid_ticker(self, mock_urlopen):
        ticker = 'AMZNN'
        dt = datetime.datetime(2019, 8, 23)
        scraper = Scraper('yahoo')

        mock_urlopen.return_value.__enter__.return_value.status = 404

        with self.assertRaises(InvalidTickerError):
            results = scraper.scrape_equity_data(ticker, dt)

class EquityDataTests(unittest.TestCase):

    def test_defaults_fields_to_zero(self):
        d = EquityData()
        self.assertEqual(d.open, 0)
        self.assertEqual(d.high, 0)
        self.assertEqual(d.low, 0)
        self.assertEqual(d.close, 0)
        self.assertEqual(d.adj_close, 0)
        self.assertEqual(d.volume, 0)

    def test_all_fields_price_fields_are_decimals(self):
        d = EquityData()
        self.assertIsInstance(d.open, Decimal)
        self.assertIsInstance(d.high, Decimal)
        self.assertIsInstance(d.low, Decimal)
        self.assertIsInstance(d.close, Decimal)
        self.assertIsInstance(d.adj_close, Decimal)

    def test_volume_field_is_an_integer(self):
        d = EquityData(volume=400.5)
        self.assertIsInstance(d.volume, int)

    def test_two_equity_data_objects_equal(self):
        d1 = EquityData(open=10, high=15.5, low=9.1, close=12.33,
                       adj_close=12.33, volume=32000)
        d2 = EquityData(open=10, high=15.5, low=9.1, close=12.33,
                       adj_close=12.33, volume=32000)
        self.assertEqual(d1, d2)

    def test_two_equity_data_objects_not_equal(self):
        d1 = EquityData(open=10, high=15.5, low=9.1, close=12.33,
                       adj_close=12.33, volume=32000)
        d2 = EquityData(open=1, high=5.5, low=0.1, close=1.28,
                       adj_close=1.28, volume=2240)
        self.assertNotEqual(d1, d2)

if __name__ == '__main__':
    unittest.main()
