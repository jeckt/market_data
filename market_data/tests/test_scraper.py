#!/usr/bin/env python

import os
import sys
import inspect
file_path = os.path.dirname(inspect.getfile(inspect.currentframe()))
sys.path.insert(0, os.path.split(os.path.split(file_path)[0])[0])

import unittest
from unittest.mock import patch
import datetime

from market_data.scraper import Scraper, InvalidSourceError
from market_data.data import EquityData, InvalidTickerError, InvalidDateError
from market_data.data import EmptyDateListError
import market_data.tests.utils as test_utils

class ScraperTests(unittest.TestCase):

    def test_scrape_from_valid_source(self):
        scraper = Scraper('yahoo')
        self.assertIsInstance(scraper, Scraper)
        self.assertEqual(scraper.source, 'yahoo')

    def test_invalid_source_scrape_error(self):
        with self.assertRaises(InvalidSourceError):
            scraper = Scraper('google')

def load_test_data():
    test_file = r'market_data/tests/amzn_scrape_test_data.html'
    with open(test_file, 'rb') as f:
        data = f.read()

    return data

class ScraperYahooEquityPricesTests(unittest.TestCase):

    @patch('urllib.request.urlopen', autospec=True)
    def test_scrape_returns_correct_equity_data(self, mock_urlopen):
        ticker, dt, expected_data = test_utils.get_expected_equity_data()
        scraper = Scraper('yahoo')

        mock_urlopen_context = mock_urlopen.return_value.__enter__.return_value
        mock_urlopen_context.status = 200
        mock_urlopen_context.read.return_value = load_test_data()

        results = scraper.scrape_equity_data(ticker, dt)

        self.assertIsInstance(results, EquityData)
        self.assertEqual(results, expected_data,
                         msg=f'res: {results} != ex: {expected_data}')

    @patch('urllib.request.urlopen', autospec=True)
    def test_scrape_equity_data_with_date_and_time(self, mock_urlopen):
        ticker, dt, expected_data = test_utils.get_expected_equity_data()
        scraper = Scraper('yahoo')

        dt = datetime.datetime(dt.year, dt.month, dt.day, 19, 35, 33)

        mock_urlopen_context = mock_urlopen.return_value.__enter__.return_value
        mock_urlopen_context.status = 200
        mock_urlopen_context.read.return_value = load_test_data()

        results = scraper.scrape_equity_data(ticker, dt)

        self.assertIsInstance(results, EquityData)
        self.assertEqual(results, expected_data,
                         msg=f'res: {results} != ex: {expected_data}')

    @patch('urllib.request.urlopen', autospec=True)
    def test_scrape_invalid_date(self, mock_urlopen):
        ticker = 'AMZN'
        dt = datetime.datetime(2019, 9, 3)
        scraper = Scraper('yahoo')

        mock_urlopen_context = mock_urlopen.return_value.__enter__.return_value
        mock_urlopen_context.status = 200
        mock_urlopen_context.read.return_value = load_test_data()

        with self.assertRaises(InvalidDateError):
            results = scraper.scrape_equity_data(ticker, dt)

    @patch('urllib.request.urlopen', autospec=True)
    def test_scrape_invalid_ticker(self, mock_urlopen):
        ticker = 'AMZNN'
        dt = datetime.datetime(2019, 8, 23)
        scraper = Scraper('yahoo')

        mock_urlopen_context = mock_urlopen.return_value.__enter__.return_value
        mock_urlopen_context.read.return_value = b''

        with self.assertRaises(InvalidTickerError):
            results = scraper.scrape_equity_data(ticker, dt)

    @patch('urllib.request.urlopen', autospec=True)
    def test_scrape_page_found_but_invalid_ticker(self, mock_urlopen):
        ticker = 'AMZNN'
        dt = datetime.datetime(2019, 8, 23)
        scraper = Scraper('yahoo')

        mock_urlopen_context = mock_urlopen.return_value.__enter__.return_value
        mock_urlopen_context.status = 200
        mock_urlopen_context.read.return_value = b'<HTML><body></body></HTML>'

        with self.assertRaises(InvalidTickerError):
            results = scraper.scrape_equity_data(ticker, dt)

class ScraperYahooEquityMultipleDatesTests(unittest.TestCase):

    @patch('urllib.request.urlopen', autospec=True)
    def setUp(self, mock_urlopen):
        self.ticker = 'AMZN'
        self.scraper = Scraper('yahoo')
        self.mock_urlopen = mock_urlopen.return_value.__enter__.return_value

    def test_scrape_invalid_ticker(self):
        ticker = 'AMZNN'
        dt = datetime.datetime(2019, 8, 23)

        self.mock_urlopen.read.return_value = b''

        with self.assertRaises(InvalidTickerError):
            _, _ = self.scraper.scrape_eq_multiple_dates(ticker, [dt])

    def test_scraper_empty_date_list_input(self):
        self.mock_urlopen.status = 200
        self.mock_urlopen.read.return_value = load_test_data()
        with self.assertRaises(EmptyDateListError):
            _, _ = self.scraper.scrape_eq_multiple_dates(self.ticker, [])

if __name__ == '__main__':
    unittest.main()
