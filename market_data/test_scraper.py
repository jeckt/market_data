#!/usr/bin/env python

import unittest
from unittest.mock import patch
import datetime

import market_data.MarketData as MarketData

class ScraperTests(unittest.TestCase):

    def test_scrape_equity_price_from_yahoo(self):
        ticker = 'AMZN'
        dt = datetime.datetime(2019, 8, 23)

        scaper = Scraper('yahoo')
        results = scraper.scrape_equity_data(ticker, dt)

        self.assertIsInstance(results, EquityData)
