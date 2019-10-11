#!/usr/bin/env python

import os
import sys
import inspect
file_path = os.path.dirname(inspect.getfile(inspect.currentframe()))
sys.path.insert(0, os.path.split(os.path.split(file_path)[0])[0])

import unittest
import datetime

from parameterized import parameterized_class

import market_data
import market_data.data_adapter as data_adapter
from market_data.data import EquityData, InvalidTickerError, InvalidDateError
import market_data.tests.utils as test_utils

class DataAdapterSourceTests(unittest.TestCase):

    def test_invalid_data_adapter_source_raises_error(self):
        with self.assertRaises(data_adapter.InvalidDataAdapterSourceError):
            data_adapter.get_adapter('invalid_source')

    def test_get_json_data_adapter_source(self):
        da = data_adapter.get_adapter(data_adapter.DataAdapterSource.JSON)
        self.assertEqual(da, market_data.json_data_adapter.JsonDataAdapter)

    def test_get_sqlite3_data_adapter_source(self):
        da = data_adapter.get_adapter(data_adapter.DataAdapterSource.SQLITE3)
        self.assertTrue(da, market_data.sqlite3_data_adapter.Sqlite3DataAdapter)

@parameterized_class(('data_adapater_source', ),[
    [data_adapter.DataAdapterSource.JSON, ],
    [data_adapter.DataAdapterSource.SQLITE3, ]
])
class DataAdapterTests(unittest.TestCase):

    def setUp(self):
        self.da = data_adapter.get_adapter(self.data_adapater_source)

    def tearDown(self):
        # NOTE(steve): I think it is acceptable to suppress
        # the error here as we only want to make sure the 
        # database is removed after each test and at the
        # same time we want to abstract the implementation
        try:
            self.da.delete_test_database()
        except:
            pass

    def test_create_test_database(self):
        self.assertFalse(os.path.isfile(self.da.test_database))
        self.da.create_test_database()
        self.assertTrue(os.path.isfile(self.da.test_database))

    def test_delete_test_database(self):
        self.da.create_test_database()
        self.assertTrue(os.path.isfile(self.da.test_database))
        self.da.delete_test_database()
        self.assertFalse(os.path.isfile(self.da.test_database))

    def test_create_existing_test_database_raises_error(self):
        self.da.create_test_database()
        with self.assertRaises(data_adapter.DatabaseExistsError):
            self.da.create_test_database()

    def test_delete_non_existing_test_database_raises_error(self):
        self.assertFalse(os.path.isfile(self.da.test_database))
        with self.assertRaises(data_adapter.DatabaseNotFoundError):
            self.da.delete_test_database()

    def test_connect_to_test_database(self):
        self.da.create_test_database()
        self.assertTrue(os.path.isfile(self.da.test_database))
        da = self.da.connect(self.da.test_database)
        self.assertEqual(da.conn_string, self.da.test_database)

    def test_connect_to_non_existing_database_throws_error(self):
        self.assertFalse(os.path.isfile('newdb.json'))
        with self.assertRaises(data_adapter.DatabaseNotFoundError):
            self.da.connect('newdb.json')

@parameterized_class(('data_adapater_source', ),[
    [data_adapter.DataAdapterSource.JSON, ],
    [data_adapter.DataAdapterSource.SQLITE3, ]
])
class DataAdapterSecuritiesTests(unittest.TestCase):

    def setUp(self):
        self.da = data_adapter.get_adapter(self.data_adapater_source)
        self.da.create_test_database()
        self.database = self.da.connect(self.da.test_database)

    def tearDown(self):
        self.database.close()
        try:
            self.da.delete_test_database()
        except:
            pass

    def test_get_securities_on_new_database_returns_empty_list(self):
        tickers = self.database.get_securities_list()
        self.assertEqual([], tickers)

    def test_insert_securities_adds_securities_to_list(self):
        tickers = self.database.get_securities_list()
        self.assertEqual([], tickers)
        new_tickers = ['AMZN', 'TLS.AX']

        self.database.insert_securities(new_tickers)

        tickers = self.database.get_securities_list()
        self.assertEqual(set(new_tickers), set(tickers))

    def test_insert_securities_duplicate_securities_inserted(self):
        tickers = self.database.get_securities_list()
        self.assertEqual([], tickers)
        new_tickers = ['AMZN', 'TLS.AX', 'AMZN']
        expected_tickers = ['AMZN', 'TLS.AX']

        self.database.insert_securities(new_tickers)

        tickers = self.database.get_securities_list()
        self.assertEqual(len(expected_tickers), len(tickers))

        # NOTE(steve): try to add an existing ticker
        new_tickers = ['TLS.AX']

        self.database.insert_securities(new_tickers)

        tickers = self.database.get_securities_list()
        self.assertEqual(len(expected_tickers), len(tickers))

    def test_update_equity_data_for_security_not_in_list_raises_error(self):
        ticker = 'AMZN'
        with self.assertRaises(InvalidTickerError):
            self.database.update_market_data(ticker, None)

    def test_insert_duplicate_security_does_not_erase_existing_data(self):
        ticker = 'AMZN'
        self.database.insert_securities([ticker])
        test_data = test_utils.load_test_data()

        dt = datetime.datetime(2019, 8, 27)
        expected_data = test_utils.get_test_data(test_data, ticker, dt)

        self.database.update_market_data(ticker, (dt, expected_data))

        actual_data = self.database.get_equity_data(ticker, dt)
        self.assertEqual(expected_data, actual_data)

        self.database.insert_securities([ticker])

        actual_data = self.database.get_equity_data(ticker, dt)
        self.assertEqual(expected_data, actual_data)

    def test_update_equity_data(self):
        ticker, dt, expected_data = test_utils.get_expected_equity_data()
        self.database.insert_securities([ticker])

        self.database.update_market_data(ticker, (dt, expected_data))

        actual_data = self.database.get_equity_data(ticker, dt)
        self.assertEqual(expected_data, actual_data)

    # NOTE(steve): multiple dates and securities are not duplications
    # of the market_data.py unit tests as these do not make calls
    # to get the data but assumes the data is provided in the correct form
    def test_get_equity_data_after_multiple_dates_updates(self):
        ticker = 'AMZN'
        self.database.insert_securities([ticker])

        test_data = test_utils.load_test_data()
        dt_1 = datetime.datetime(2019, 8, 27)
        expected_data_1 = test_utils.get_test_data(test_data, ticker, dt_1)
        self.database.update_market_data(ticker, (dt_1, expected_data_1))

        dt_2 = datetime.datetime(2019, 8, 26)
        expected_data_2 = test_utils.get_test_data(test_data, ticker, dt_2)
        self.database.update_market_data(ticker, (dt_2, expected_data_2))

        actual_data_2 = self.database.get_equity_data(ticker, dt_2)
        self.assertEqual(expected_data_2, actual_data_2)

        actual_data_1 = self.database.get_equity_data(ticker, dt_1)
        self.assertEqual(expected_data_1, actual_data_1)

        # NOTE(steve): should this be in its own test case???
        data_series = self.database.get_equity_data_series(ticker)
        self.assertEqual(len(data_series), 2)

        self.assertEqual(dt_1, data_series[0][0])
        self.assertEqual(expected_data_1, data_series[0][1])

        self.assertEqual(dt_2, data_series[1][0])
        self.assertEqual(expected_data_2, data_series[1][1])

    def test_equity_date_series_invalid_ticker_error(self):
        with self.assertRaises(InvalidTickerError):
            self.database.get_equity_data_series('AMZN')

    def test_get_equity_data_for_multiple_securities(self):
        self.database.insert_securities(['AMZN', 'GOOG'])
        dt = datetime.datetime(2019, 8, 27)

        test_data = test_utils.load_test_data()
        expected_data_1 = test_utils.get_test_data(test_data, 'AMZN', dt)
        self.database.update_market_data('AMZN', (dt, expected_data_1))

        expected_data_2 = test_utils.get_test_data(test_data, 'GOOG', dt)
        self.database.update_market_data('GOOG', (dt, expected_data_2))

        actual_data_2 = self.database.get_equity_data('GOOG', dt)
        self.assertEqual(expected_data_2, actual_data_2)

        actual_data_1 = self.database.get_equity_data('AMZN', dt)
        self.assertEqual(expected_data_1, actual_data_1)

    def test_get_equity_data_for_invalid_ticker_raises_error(self):
        ticker = 'AMZN'
        dt = datetime.datetime(2019, 8, 27)

        with self.assertRaises(InvalidTickerError):
            self.database.get_equity_data(ticker, dt)

    def test_get_equity_data_for_invalid_date_raises_error(self):
        ticker = 'AMZN'
        self.database.insert_securities([ticker])
        dt = datetime.datetime(2019, 8, 27)

        with self.assertRaises(InvalidDateError):
            self.database.get_equity_data(ticker, dt)

if __name__ == '__main__':
    unittest.main()
