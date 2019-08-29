#!/usr/bin/env python

import unittest
from unittest import skip
from unittest.mock import patch
import datetime

from scraper import Scraper, EquityData
from scraper import InvalidSourceError, InvalidTickerError

class ScraperTests(unittest.TestCase):

    def test_scrape_from_valid_source(self):
        scraper = Scraper('yahoo')
        self.assertIsInstance(scraper, Scraper)
        self.assertEqual(scraper.source, 'yahoo')

    def test_invalid_source_scrape_error(self):
        with self.assertRaises(InvalidSourceError):
            scraper = Scraper('google')

class ScraperYahooEquityPricesTests(unittest.TestCase):

    @patch('urllib.request.urlopen', autospec=True)
    def test_scrape_returns_data_object(self, mock_urlopen):
        ticker = 'AMZN'
        dt = datetime.datetime(2019, 8, 23)
        scraper = Scraper('yahoo')

        mock_urlopen.return_value.__enter__.return_value.status = 200

        results = scraper.scrape_equity_data(ticker, dt)

        self.assertIsInstance(results, EquityData)

    @patch('urllib.request.urlopen', autospec=True)
    def test_scrape_invalid_ticker(self, mock_urlopen):
        ticker = 'AMZNN'
        dt = datetime.datetime(2019, 8, 23)
        scraper = Scraper('yahoo')

        mock_urlopen.return_value.__enter__.return_value.status = 404

        with self.assertRaises(InvalidTickerError):
            results = scraper.scrape_equity_data(ticker, dt)

if __name__ == '__main__':
    unittest.main()
