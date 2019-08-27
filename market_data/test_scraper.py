#!/usr/bin/env python

import unittest
from unittest.mock import patch
import datetime

import scraper as Scraper
from scraper import InvalidSourceError

class ScraperTests(unittest.TestCase):

    def test_scrape_from_valid_source(self):
        scraper = Scraper('yahoo')
        self.assertIsInstance(scraper, Scraper)

    def test_invalid_source_scrape_error(self):
        with self.assertRaises(InvalidSourceError):
            scraper = Scraper('google')

    def test_scrape_equity_price_from_yahoo(self):
        ticker = 'AMZN'
        dt = datetime.datetime(2019, 8, 23)

        scaper = Scraper('yahoo')
        results = scraper.scrape_equity_data(ticker, dt)

        self.assertIsInstance(results, EquityData)
