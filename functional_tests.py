#!/usr/bin/env python

import unittest
import datetime
from market_data.market_data import MarketData

# NOTE(steve): Other tests I can think of
# 1. Load app and retreive an fx rate on a given day
# 2. Load equity price over multiple days
# 3. Load fx rate over multiple days

class FunctionalTests(unittest.TestCase):

    def test_user_loads_app_and_retreives_equity_price(self):
        # Jack opens the application
        md = MarketData()
        md.run()

        # Jack wants to know to know what the closing price
        # of his Amazon stock is on the 23rd August 2019
        dt = datetime.datetime(2019, 8, 23)
        data = md.get_equity_data('AMZN', dt)

        # He verifies that the price is what he remembers it
        # to be when he checked yesterday.
        self.assertEqual(data.close, 1768.87)

        # Happy with the results he closes the app
        md.close()

if __name__ == '__main__':
    unittest.main()
