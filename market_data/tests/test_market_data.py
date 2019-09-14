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
from market_data.data import InvalidTickerError, InvalidDateError
from market_data.data_adapter import DataAdapter, DatabaseNotFoundError
from market_data.tests.utils import get_expected_equity_data

class MarketDataTests(unittest.TestCase):

    def setUp(self):
        self.database = DataAdapter.test_database
        DataAdapter.create_test_database()
        self.app = MarketData()
        self.app.run(database=self.database)

    def tearDown(self):
        self.app.close()
        try:
            DataAdapter.delete_test_database()
        except:
            pass

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
        self.database = DataAdapter.test_database
        DataAdapter.create_test_database()
        self.app = MarketData()
        self.app.run(database=self.database)

    def tearDown(self):
        self.app.close()
        try:
            DataAdapter.delete_test_database()
        except:
            pass

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
        ticker, dt, expected_data = get_expected_equity_data()
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

    @patch('market_data.scraper.Scraper.scrape_equity_data', autospec=True)
    def test_get_equity_data_for_multiple_dates(self, mock_scraper):
        ticker = 'AMZN'
        self.app.add_security(ticker)

        with open('market_data/tests/test_data.json', 'r') as db:
            test_data = json.load(db)

        dict_data = test_data[ticker]['27-Aug-2019']
        expected_data_1 = EquityData(
            open=dict_data['open'],
            high=dict_data['high'],
            low=dict_data['low'],
            close=dict_data['close'],
            adj_close=dict_data['adj_close'],
            volume=dict_data['volume']
        )
        mock_scraper.return_value = expected_data_1
        self.app.update_market_data(ticker, datetime.datetime(2019, 8, 27))

        dict_data = test_data[ticker]['26-Aug-2019']
        expected_data_2 = EquityData(
            open=dict_data['open'],
            high=dict_data['high'],
            low=dict_data['low'],
            close=dict_data['close'],
            adj_close=dict_data['adj_close'],
            volume=dict_data['volume']
        )
        mock_scraper.return_value = expected_data_2
        self.app.update_market_data(ticker, datetime.datetime(2019, 8, 26))

        self.app.close()

        new_app = MarketData()
        new_app.run(database=self.database)

        actual_data_2 = new_app.get_equity_data(ticker,
                                                datetime.datetime(2019, 8, 26))
        self.assertEqual(expected_data_2, actual_data_2)

        actual_data_1 = new_app.get_equity_data(ticker,
                                                datetime.datetime(2019, 8, 27))
        self.assertEqual(expected_data_1, actual_data_1)

    @patch('market_data.scraper.Scraper.scrape_equity_data', autospec=True)
    def test_get_equity_data_for_multiple_securities(self, mock_scraper):
        dt = datetime.datetime(2019, 8, 27)
        self.app.add_security('AMZN')
        self.app.add_security('GOOG')

        with open('market_data/tests/test_data.json', 'r') as db:
            test_data = json.load(db)

        dict_data = test_data['AMZN']['27-Aug-2019']
        expected_data_1 = EquityData(
            open=dict_data['open'],
            high=dict_data['high'],
            low=dict_data['low'],
            close=dict_data['close'],
            adj_close=dict_data['adj_close'],
            volume=dict_data['volume']
        )
        mock_scraper.return_value = expected_data_1
        self.app.update_market_data('AMZN', dt)

        dict_data = test_data['GOOG']['27-Aug-2019']
        expected_data_2 = EquityData(
            open=dict_data['open'],
            high=dict_data['high'],
            low=dict_data['low'],
            close=dict_data['close'],
            adj_close=dict_data['adj_close'],
            volume=dict_data['volume']
        )
        mock_scraper.return_value = expected_data_2
        self.app.update_market_data('GOOG', dt)

        self.app.close()

        new_app = MarketData()
        new_app.run(database=self.database)

        actual_data_2 = new_app.get_equity_data('GOOG', dt)
        self.assertEqual(expected_data_2, actual_data_2)

        actual_data_1 = new_app.get_equity_data('AMZN', dt)
        self.assertEqual(expected_data_1, actual_data_1)

class EquityDataTests(unittest.TestCase):

    def setUp(self):
        self.database = DataAdapter.test_database
        DataAdapter.create_test_database()
        self.app = MarketData()
        self.app.run(database=self.database)

    def tearDown(self):
        self.app.close()
        try:
            DataAdapter.delete_test_database()
        except:
            pass

    def test_get_equity_data_on_security_not_in_list(self):
        with self.assertRaises(InvalidTickerError):
            self.app.get_equity_data('AMZN', datetime.datetime(2019, 8, 27))

    def test_get_equity_data_on_invalid_date(self):
        self.app.add_security('AMZN')
        with self.assertRaises(InvalidDateError):
            self.app.get_equity_data('AMZN', datetime.datetime(2019, 8, 27))

    @patch('market_data.scraper.Scraper.scrape_equity_data', autospec=True)
    def test_invalid_ticker_in_update_market_data(self, mock_scraper):
        self.app.add_security('AMZNN')

        mock_scraper.side_effect = InvalidTickerError
        with self.assertRaises(InvalidTickerError):
            self.app.update_market_data('AMZNN', datetime.datetime(2019, 8, 27))

    @patch('market_data.scraper.Scraper.scrape_equity_data', autospec=True)
    def test_invalid_date_in_update_market_data(self, mock_scraper):
        self.app.add_security('AMZN')

        mock_scraper.side_effect = InvalidDateError
        with self.assertRaises(InvalidDateError):
            self.app.update_market_data('AMZN', datetime.datetime(2017, 8, 25))

    def test_update_market_data_on_security_not_in_list(self):
        ticker = 'AMZN'
        dt = datetime.datetime(2019, 8, 27)
        with self.assertRaises(InvalidTickerError):
            self.app.update_market_data(ticker, dt)

    # TODO(steve): should we split these two tests by
    # injecting the market data directly into the test database???
    def test_update_market_data_and_get_equity_data(self):
        ticker, dt, expected_data = get_expected_equity_data()
        self.app.add_security(ticker)

        mock_method = 'market_data.scraper.Scraper.scrape_equity_data'
        with patch(mock_method, autospec=True) as mock_scraper:
            mock_scraper.return_value = expected_data
            self.app.update_market_data(ticker, dt)

        actual_data = self.app.get_equity_data(ticker, dt)
        self.assertEqual(expected_data, actual_data)

if __name__ == '__main__':
    unittest.main()
