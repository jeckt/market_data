#!/usr/bin/env python

import unittest
from unittest import skip
from unittest.mock import patch, Mock
import datetime

from market_data.market_data import MarketData
from market_data.data import EquityData
from market_data.data import InvalidTickerError, InvalidDateError
import market_data.data_adapter as data_adapter
import market_data.tests.utils as test_utils

class FunctionalTests(unittest.TestCase):

    def setUp(self):
        self.test_data = test_utils.load_test_data()
        self.da = data_adapter.get_adapter(data_adapter.DataAdapterSource.JSON)
        self.database = self.da.test_database
        self.da.create_test_database()

    def tearDown(self):
        try:
            self.da.delete_test_database()
        except:
            pass

    @patch('market_data.scraper.Scraper.scrape_equity_data', autospec=True)
    def test_can_get_equity_data_after_multiple_updates(self, mock_scrape):
        # Carol once again opens up the application and 
        # adds a couple of securities into the app.
        app = MarketData()
        app.run(database=self.database)
        new_tickers = ['AMZN', 'GOOG']
        for ticker in new_tickers:
            app.add_security(ticker)

        # proceeds to update the data in the application
        # for multiple dates and securities
        for ticker in new_tickers:
            data = self.test_data[ticker]
            for date_string in data:
                dt = datetime.datetime.strptime(date_string, '%d-%b-%Y')
                equity_data = test_utils.get_test_data(self.test_data,
                                                       ticker, dt)
                mock_scrape.return_value = equity_data
                app.update_market_data(ticker, dt)

        # Satisfied that she has updated all she needs to
        # she closes the application down.
        app.close()

        # Josh, her ever inquistive friend checks in on
        # the prices of AMZN and GOOG.
        new_app = MarketData()
        new_app.run(database=self.database)

        # He first checks the prices for GOOG first
        dt = datetime.datetime(2019, 8, 27)
        expected_data = test_utils.get_test_data(self.test_data, 'GOOG', dt)
        actual_data = new_app.get_equity_data('GOOG', dt)
        self.assertEqual(expected_data, actual_data, 'GOOG: 27-Aug-2019')

        # He then checks the prices for AMZN on both dates
        expected_data = test_utils.get_test_data(self.test_data, 'AMZN', dt)
        actual_data = new_app.get_equity_data('AMZN', dt)
        self.assertEqual(expected_data, actual_data, 'AMZN: 27-Aug-2019')

        dt = datetime.datetime(2019, 8, 26)
        expected_data = test_utils.get_test_data(self.test_data, 'AMZN', dt)
        actual_data = new_app.get_equity_data('AMZN', dt)
        self.assertEqual(expected_data, actual_data, 'AMZN: 26-Aug-2019')

        # Satisfied with what he sees he closes the app
        new_app.close()

    @patch('market_data.scraper.Scraper.scrape_equity_data', autospec=True)
    def test_can_retreive_equity_data_on_app_reopen(self, mock_scrape):
        # Carol opens up the application and add
        # adds Amazon (AMZN) to the list of
        # securities she wants to start tracking
        # and then closes the app.
        app = MarketData()
        app.run(database=self.database)
        new_tickers = ['AMZN', 'TLS.AX']
        for ticker in new_tickers:
            app.add_security(ticker)
        app.close()

        # Jarvis opens up the application and
        # goes through the list of securities
        # and updates them for the latest
        # market data
        app2 = MarketData()
        app2.run(database=self.database)
        tickers = app2.get_securities_list()
        self.assertEqual(set(new_tickers), set(tickers))

        dt = datetime.datetime(2019, 8, 27)
        expected_data = test_utils.get_test_data(self.test_data, 'AMZN', dt)
        mock_scrape.return_value = expected_data
        for ticker in tickers:
            app2.update_market_data(ticker, dt)

        app2.close()

        # Josh now opens the app to checks today's closing
        # price of Amazon after he comes back from work
        app3 = MarketData()
        app3.run(database=self.database)
        actual_data = app3.get_equity_data('AMZN', dt)
        self.assertEqual(expected_data, actual_data)
        app3.close()

    def test_add_security_into_app(self):
        # Carol opens up the application
        app = MarketData()
        app.run(database=self.database)

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

    @patch('market_data.scraper.Scraper.scrape_equity_data', autospec=True)
    def test_get_equity_data_from_app(self, mock_scrape):
        # Josh has heard of this new app from 
        # Carol and decides to open the app
        # and play with it.
        app = MarketData()
        app.run(database=self.database)

        # Carol told Josh that she has already
        # added a security into the app
        ticker = 'AMZN'
        dt = datetime.datetime(2019, 8, 27)
        app.add_security(ticker)

        # Josh proceeds to check what the security price 
        # on the 31 July 2019 is of the stock Carol added
        # but accidentally enters the wrong ticker name
        with self.assertRaises(InvalidTickerError):
            data = app.get_equity_data('AMZNN', dt)

        # He then tries again but with the correct
        # ticker this time but with the wrong date..
        with self.assertRaises(InvalidDateError):
            data = app.get_equity_data(ticker, datetime.datetime(2017, 8, 25))

        # Third time lucky, he enters in the correct
        # ticker and date and gets the results!
        expected_data = test_utils.get_test_data(self.test_data, ticker, dt)
        mock_scrape.return_value = expected_data
        app.update_market_data(ticker, dt)

        data = app.get_equity_data(ticker, dt)

        # He then goes to his trusty source, Yahoo to
        # confirm that the security price is indeed correct.
        self.assertEqual(data, expected_data)

if __name__ == '__main__':
    unittest.main()
