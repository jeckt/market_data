#!/usr/bin/env python

import unittest
from unittest import skip
from unittest.mock import patch
import datetime

from scraper import Scraper, InvalidSourceError

class ScraperTests(unittest.TestCase):

    def test_scrape_from_valid_source(self):
        scraper = Scraper('yahoo')
        self.assertIsInstance(scraper, Scraper)
        self.assertEqual(scraper.source, 'yahoo')

    def test_invalid_source_scrape_error(self):
        with self.assertRaises(InvalidSourceError):
            scraper = Scraper('google')

    def test_scrape_equity_price_from_yahoo_returns_equity_data(self):
        ticker = 'AMZN'
        dt = datetime.datetime(2019, 8, 23)

        scraper = Scraper('yahoo')
        results = scraper.scrape_equity_data(ticker, dt)

        self.assertIsInstance(results, EquityData)

if __name__ == '__main__':
    unittest.main()
