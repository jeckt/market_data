#!/usr/bin/env python

import os
import sys
import inspect
file_path = os.path.dirname(inspect.getfile(inspect.currentframe()))
sys.path.insert(0, os.path.split(os.path.split(file_path)[0])[0])

import unittest
from unittest import skip
from unittest.mock import patch
import datetime
import json

from market_data.market_data import MarketData
from market_data.market_data import NotInitialisedError
from market_data.data import EquityData
from market_data.data import InvalidTickerError, InvalidDateError, NoDataError
from market_data.data_adapter import DataAdapter, DatabaseNotFoundError
import market_data.tests.utils as test_utils

def common_setup(obj):
    obj.database = DataAdapter.test_database
    DataAdapter.create_test_database()
    obj.app = MarketData()
    obj.app.run(database=obj.database)

def common_teardown(obj):
    obj.app.close()
    try:
        DataAdapter.delete_test_database()
    except:
        pass

class MarketDataTests(unittest.TestCase):

    def setUp(self):
        common_setup(self)

    def tearDown(self):
        common_teardown(self)

    # TODO(steve): Is there are better way to test a set of 
    # methods are only accessible when class is initialised
    def test_app_not_initialised_before_use_raises_error(self):
        app = MarketData()

        with self.assertRaises(NotInitialisedError):
            app.add_security('AMZN')

        with self.assertRaises(NotInitialisedError):
            sec_list = app.get_securities_list()

    # NOTE(steve): Testing two functions instead of each 
    # individually as individual tests will require
    # knowledge of the implementation.
    def test_add_and_get_securities_list(self):
        self.app.add_security('AMZN')
        actual_sec_list = self.app.get_securities_list()
        self.assertEqual(actual_sec_list, ['AMZN'])

        self.app.add_security('GOOG')
        actual_sec_list = set(self.app.get_securities_list())
        self.assertEqual(actual_sec_list, set(['AMZN', 'GOOG']))

    def test_not_initialised_error_after_app_close(self):
        self.app.add_security('AMZN')
        self.app.close()

        with self.assertRaises(NotInitialisedError):
            self.app.add_security('GOOG')

class MarketDataPersistentStorageTests(unittest.TestCase):

    def setUp(self):
        common_setup(self)

    def tearDown(self):
        common_teardown(self)

    def test_added_security_is_in_list_on_reopen(self):
        ticker = 'TLS'
        self.app.add_security(ticker)
        self.app.close()

        new_app = MarketData()
        new_app.run(database=self.database)
        tickers = new_app.get_securities_list()
        new_app.close()
        self.assertEqual([ticker], tickers)

    def test_create_production_database_by_default(self):
        self.assertEqual([], self.app.get_securities_list())

    def test_raise_database_not_found_error(self):
        with self.assertRaises(DatabaseNotFoundError):
            self.app.run(database='db.json')

    @patch('market_data.data_adapter.DataAdapter.close', autospec=True)
    def test_data_adaptor_closed_on_app_close(self, mock_close):
        self.app.close()
        mock_close.assert_called_once()

    def test_get_equity_data_on_app_reopen(self):
        ticker, dt, expected_data = test_utils.get_expected_equity_data()
        self.app.add_security(ticker)

        mock_method = 'market_data.scraper.Scraper.scrape_equity_data'
        with patch(mock_method, autospec=True) as mock_scraper:
            mock_scraper.return_value = expected_data
            self.app.update_market_data(ticker, dt)

        actual_data = self.app.get_equity_data(ticker, dt)
        self.assertEqual(expected_data, actual_data)
        self.app.close()

        new_app = MarketData()
        new_app.run(database=self.database)
        actual_data = new_app.get_equity_data(ticker, dt)
        self.assertEqual(expected_data, actual_data)
        new_app.close()

class EquityDataTests(unittest.TestCase):

    def setUp(self):
        common_setup(self)
        self.ticker = 'AMZN'
        self.test_date = datetime.datetime(2019, 8, 27)

    def tearDown(self):
        common_teardown(self)

    def update_with_test_data(self, params, mock_scraper):
        test_data = test_utils.load_test_data()

        expected_data = []
        for ticker, dt in params:
            data = test_utils.get_test_data(test_data, ticker, dt)
            mock_scraper.return_value = data
            self.app.update_market_data(ticker, dt)
            expected_data.append(data)

        return expected_data

    def check_equity_data(self, params, expected_data):
        for (ticker, dt), expected in zip(params, expected_data):
            actual = new_app.get_equity_data(ticker, dt)
            self.assertEqual(expected, actual)

    def test_get_equity_data_on_security_not_in_list(self):
        with self.assertRaises(InvalidTickerError):
            self.app.get_equity_data(self.ticker, self.test_date)

    def test_get_equity_data_on_invalid_date(self):
        self.app.add_security(self.ticker)
        with self.assertRaises(InvalidDateError):
            self.app.get_equity_data(self.ticker, self.test_date)

    @patch('market_data.scraper.Scraper.scrape_equity_data', autospec=True)
    def test_invalid_ticker_in_update_market_data(self, mock_scraper):
        self.app.add_security('AMZNN')

        mock_scraper.side_effect = InvalidTickerError
        with self.assertRaises(InvalidTickerError):
            self.app.update_market_data('AMZNN', self.test_date)

    @patch('market_data.scraper.Scraper.scrape_equity_data', autospec=True)
    def test_invalid_date_in_update_market_data(self, mock_scraper):
        self.app.add_security(self.ticker)

        mock_scraper.side_effect = InvalidDateError
        with self.assertRaises(InvalidDateError):
            self.app.update_market_data(self.ticker, self.test_date)

    def test_update_market_data_on_security_not_in_list(self):
        with self.assertRaises(InvalidTickerError):
            self.app.update_market_data(self.ticker, self.test_date)

    # TODO(steve): should we split these two tests by
    # injecting the market data directly into the test database???
    def test_update_market_data_and_get_equity_data(self):
        ticker, dt, expected_data = test_utils.get_expected_equity_data()
        self.app.add_security(ticker)

        mock_method = 'market_data.scraper.Scraper.scrape_equity_data'
        with patch(mock_method, autospec=True) as mock_scraper:
            mock_scraper.return_value = expected_data
            self.app.update_market_data(ticker, dt)

        actual_data = self.app.get_equity_data(ticker, dt)
        self.assertEqual(expected_data, actual_data)

    @patch('market_data.scraper.Scraper.scrape_equity_data', autospec=True)
    def test_get_equity_data_for_multiple_dates(self, mock_scraper):
        self.app.add_security(self.ticker)

        dt = [datetime.datetime(2019, 8, 27), datetime.datetime(2019, 8, 26)]
        params = zip([self.ticker] * 2, dt)
        expected_data = self.update_with_test_data(params, mock_scraper)

        self.app.close()

        new_app = MarketData()
        new_app.run(database=self.database)

        self.check_equity_data(params, expected_data)

        # NOTE(steve): should this be in a separate test???
        data_series = new_app.get_equity_data_series(self.ticker)
        self.assertEqual(len(data_series), 2)

        for i in range(2):
            self.assertEqual(dt[i], data_series[i][0])
            self.assertEqual(expected_data[i], data_series[i][1])

        new_app.close()

    @patch('market_data.scraper.Scraper.scrape_equity_data', autospec=True)
    def test_get_equity_data_for_multiple_securities(self, mock_scraper):
        dt = datetime.datetime(2019, 8, 27)
        tickers = ['AMZN', 'GOOG']
        for ticker in tickers:
            self.app.add_security(ticker)

        params = zip(tickers, [dt] * 2)
        expected_data = self.update_with_test_data(params, mock_scraper)

        self.app.close()

        new_app = MarketData()
        new_app.run(database=self.database)
        self.check_equity_data(params, expected_data)
        new_app.close()

    def test_get_equity_data_series_invalid_ticker_error(self):
        with self.assertRaises(InvalidTickerError):
            self.app.get_equity_data_series(self.ticker)

    @patch('market_data.scraper.Scraper.scrape_equity_data', autospec=True)
    def test_get_latest_equity_data_for_security(self, mock_scraper):
        self.app.add_security(self.ticker)

        test_data = test_utils.load_test_data()

        dt_1 = datetime.datetime(2019, 8, 27)
        dt_2 = datetime.datetime(2019, 8, 26)
        dt_3 = datetime.datetime(2019, 8, 23)
        dt = [dt_2, dt_1, dt_3] # not updated in order!
        params = zip([self.ticker] * 3, dt)
        expected_data = self.update_with_test_data(params, mock_scraper)

        dt, actual_data = self.app.get_latest_equity_data(self.ticker)
        self.assertEqual(dt_1, dt)
        self.assertEqual(expected_data[1], actual_data)

    def test_get_latest_equity_data_invalid_ticker_error(self):
        with self.assertRaises(InvalidTickerError):
            self.app.get_latest_equity_data(self.ticker)

    def test_get_latest_equity_data_no_data_error(self):
        self.app.add_security(self.ticker)

        with self.assertRaises(NoDataError):
            self.app.get_latest_equity_data(self.ticker)

if __name__ == '__main__':
    unittest.main()
