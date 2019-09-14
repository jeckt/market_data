#!/usr/bin/env python

import unittest
from unittest import skip
from unittest.mock import patch, Mock
import datetime
import json

from market_data.market_data import MarketData
from market_data.data import EquityData
from market_data.data import InvalidTickerError, InvalidDateError
from market_data.data_adapter import DataAdapter

class FunctionalTests(unittest.TestCase):

    def setUp(self):
        with open('market_data/tests/test_data.json', 'r') as db:
            self.test_data = json.load(db)
        self.database = DataAdapter.test_database
        DataAdapter.create_test_database()

    def tearDown(self):
        try:
            DataAdapter.delete_test_database()
        except:
            pass

    def get_test_data(self, ticker, date_string):
        data = self.test_data[ticker]
        dt = datetime.datetime.strptime(date_string, '%d-%b-%Y')
        expected_data = EquityData(
            open=data[date_string]["open"],
            high=data[date_string]["high"],
            low=data[date_string]["low"],
            close=data[date_string]["close"],
            adj_close=data[date_string]["adj_close"],
            volume=data[date_string]["volume"]
        )
        return dt, expected_data

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
                dt, expected_data = self.get_test_data(ticker, date_string)
                mock_scrape.return_value = expected_data
                app.update_market_data(ticker, dt)

        # Satisfied that she has updated all she needs to
        # she closes the application down.
        app.close()

        # Josh, her ever inquistive friend checks in on
        # the prices of AMZN and GOOG.
        new_app = MarketData()
        new_app.run(database=self.database)

        # He first checks the prices for GOOG first
        dt, expected_data = self.get_test_data('GOOG', '27-Aug-2019')
        actual_data = new_app.get_equity_data('GOOG', dt)
        self.assertEqual(expected_data, actual_data, 'GOOG: 27-Aug-2019')

        # He then checks the prices for AMZN on both dates
        dt, expected_data = self.get_test_data('AMZN', '27-Aug-2019')
        actual_data = new_app.get_equity_data('AMZN', dt)
        self.assertEqual(expected_data, actual_data, 'AMZN: 27-Aug-2019')

        dt, expected_data = self.get_test_data('AMZN', '26-Aug-2019')
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

        dt, expected_data = self.get_test_data('AMZN', '27-Aug-2019')
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

    def test_get_historical_equity_data_from_app(self):
        # Josh has heard of this new app from 
        # Carol and decides to open the app
        # and play with it.
        app = MarketData()
        app.run(database=self.database)

        # Carol told Josh that she has already
        # added a security into the app
        ticker = 'AMZN'
        dt = datetime.datetime(2019, 7, 31)
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

        # NOTE(steve) patch work so that we don't hit the external dependency
        with patch('urllib.request.urlopen', autospec=True) as mock_urlopen:
            import market_data.tests.test_scraper as sp
            load_test_data = sp.ScraperYahooEquityPricesTests.load_test_data
            mock_urlopen_stub = mock_urlopen.return_value.__enter__
            mock_urlopen_stub.return_value.read.return_value = load_test_data()

            data = app.update_market_data(ticker, dt)

        # Third time lucky, he enters in the correct
        # ticker and date and gets the results!
        data = app.get_equity_data(ticker, dt)

        # He then goes to his trusty source, Yahoo to
        # confirm that the security price is indeed correct.
        expected_data = EquityData(
            open='1898.11',
            high='1899.55',
            low='1849.44',
            close='1866.78',
            adj_close='1866.78',
            volume=4470700
        )
        self.assertEqual(data, expected_data)

if __name__ == '__main__':
    unittest.main()
