#!/usr/bin/env python

import unittest
from unittest import skip
from unittest.mock import patch
import datetime
from decimal import Decimal

from market_data.market_data import MarketData
from market_data.data import EquityData
from market_data.data import InvalidTickerError

class FunctionalTests(unittest.TestCase):

    def test_add_security_into_app(self):
        # Carol opens up the application
        app = MarketData()
        app.run()

        # Carol adds Amazon(AMZN) to the app as
        # she would like to start tracking the
        # daily market price.
        ticker = 'AMZN'
        app.add_security(ticker)

        # She then checks to make sure that
        # the actual stock has been added to
        # the list of securities
        self.assertTrue(ticker in app.get_securities_list())

        # Satisfied that it is indeed in the app
        # she closes it and gets on with her day
        app.close()

    # TODO(steve): we need another test where the
    # historical data is not available through the
    # scraper. Should that be a unit test???
    @patch('urllib.request.urlopen', autospec=True)
    def test_get_historical_equity_data_from_app(self, mock_urlopen):
        # Josh has heard of this new app from 
        # Carol and decides to open the app
        # and play with it.
        app = MarketData()
        app.run()

        # Carol told Josh that she has already
        # added a security into the app
        ticker = 'AMZN'
        dt = datetime.datetime(2019, 7, 31)
        app.add_security(ticker)

        # NOTE(steve) patch work so that we don't hit the 
        # external dependency
        import market_data.tests.test_scraper as sp
        load_test_data = sp.ScraperYahooEquityPricesTests.load_test_data
        mock_urlopen_context = mock_urlopen.return_value.__enter__.return_value
        mock_urlopen_context.read.return_value = load_test_data()

        # Josh proceeds to check what the security price 
        # on the 31 July 2019 is of the stock Carol added
        # but accidentally enters the wrong ticker name
        with self.assertRaises(InvalidTickerError):
            data = app.get_equity_data('AMZNN', dt)

        # He then tries again but with the correct
        # ticker this time but with the wrong date..
        # he wants to see into the future!
        with self.assertRaises(InvalidDateError):
            data = app.get_equity_data(ticker, datetime.datetime(2020, 7, 31))

        # Third time lucky, he enters in the correct
        # ticker and date and gets the results!
        data = app.get_equity_data(ticker, dt)

        # He then goes to his trusty source, Yahoo to
        # confirm that the security price is indeed correct.
        expected_data = EquityData()
        expected_data.open = Decimal('1898.11')
        expected_data.high = Decimal('1899.55')
        expected_data.low = Decimal('1849.44')
        expected_data.close = Decimal('1866.78')
        expected_data.adj_close = Decimal('1866.78')
        expected_data.volume = int(4470700)
        self.assertEqual(data, expected_data)

    # NOTE(steve): user is a machine that runs on a 
    # scheduler and collects the required data this
    # will be coded into a script
    # TODO(steve): a terrible functional test as
    # it does not actually test that the data
    # is correct after executing functions!!!
    @skip
    def test_update_market_data_in_app(self):
        # Jarvis (machine) opens up the application
        app = MarketData()
        app.run()

        # Jarvis gets the list of securities that
        # he needs to update
        securities = app.get_securities_list()

        # He checks that the securities in the
        # list are what he expects
        expected_sec_list = ['AMZN', 'TLS.AX']
        self.assertEqual(securities, expected_sec_list)

        # Jarvis proceeds to update each security
        # in the list with the most recent available
        # market data
        # TODO(steve): mock this so that it always 
        # returns a valid date for this test case
        dt = datetime.datetime.today()
        for sec in securities:
            app.update_security_data(sec, dt)

        # Jarvis closes the application once his
        # job is complete
        app.close()

if __name__ == '__main__':
    unittest.main()
