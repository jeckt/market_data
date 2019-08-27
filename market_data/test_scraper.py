#!/usr/bin/env python

import unittest
from unittest import skip
from unittest.mock import patch
import datetime

from scraper import Scraper, EquityData, InvalidSourceError

class ScraperTests(unittest.TestCase):

    def test_scrape_from_valid_source(self):
        scraper = Scraper('yahoo')
        self.assertIsInstance(scraper, Scraper)
        self.assertEqual(scraper.source, 'yahoo')

    def test_invalid_source_scrape_error(self):
        with self.assertRaises(InvalidSourceError):
            scraper = Scraper('google')

class ScraperYahooEquityPricesTests(unittest.TestCase):

    def test_scrape_returns_data_object(self):
        ticker = 'AMZN'
        dt = datetime.datetime(2019, 8, 23)

        scraper = Scraper('yahoo')
        results = scraper.scrape_equity_data(ticker, dt)

        self.assertIsInstance(results, EquityData)

    def test_scrape_makes_http_request(self):
        ticker = 'AMZN'
        dt = datetime.datetime(2019, 8, 23)

        scraper = Scraper('yahoo')

        with patch('urllib.request.Request') as mock_request:
            results = scraper.scrape_equity_data(ticker, dt)
            url = r'https://finance.yahoo.com/quote/{ticker}/history?p={ticker}'
            mock_request.assert_called_once_with(url)

if __name__ == '__main__':
    unittest.main()
