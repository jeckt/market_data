#!/usr/bin/env python

import os
import sys
import inspect
file_path = os.path.dirname(inspect.getfile(inspect.currentframe()))
sys.path.insert(0, os.path.split(os.path.split(file_path)[0])[0])

import unittest
from unittest import skip
import datetime
from decimal import Decimal
from market_data.data_adapter import DataAdapter, TextDataModel
from market_data.data_adapter import DatabaseExistsError, DatabaseNotFoundError
from market_data.data import EquityData, InvalidTickerError
from market_data.tests.utils import get_expected_equity_data

class DataAdapterTestDatabaseTests(unittest.TestCase):

    def tearDown(self):
        # NOTE(steve): I think it is acceptable to suppress
        # the error here as we only want to make sure the 
        # database is removed after each test and at the
        # same time we want to abstract the implementation
        try:
            DataAdapter.delete_test_database()
        except:
            pass

    def test_create_test_database(self):
        self.assertFalse(os.path.isfile(DataAdapter.test_database))
        DataAdapter.create_test_database()
        self.assertTrue(os.path.isfile(DataAdapter.test_database))

    def test_delete_test_database(self):
        DataAdapter.create_test_database()
        self.assertTrue(os.path.isfile(DataAdapter.test_database))
        DataAdapter.delete_test_database()
        self.assertFalse(os.path.isfile(DataAdapter.test_database))

    def test_create_existing_test_database_raises_error(self):
        DataAdapter.create_test_database()
        with self.assertRaises(DatabaseExistsError):
            DataAdapter.create_test_database()

    def test_delete_non_existing_test_database_raises_error(self):
        self.assertFalse(os.path.isfile(DataAdapter.test_database))
        with self.assertRaises(DatabaseNotFoundError):
            DataAdapter.delete_test_database()

    def test_connect_to_test_database(self):
        DataAdapter.create_test_database()
        self.assertTrue(os.path.isfile(DataAdapter.test_database))
        da = DataAdapter.connect(DataAdapter.test_database)
        self.assertEqual(da.conn_string, DataAdapter.test_database)

class DataAdapterTests(unittest.TestCase):

    def tearDown(self):
        if os.path.isfile(DataAdapter.prod_database):
            os.remove(DataAdapter.prod_database)

    def test_create_and_connect_to_prod_database_by_default(self):
        self.assertFalse(os.path.isfile(DataAdapter.prod_database))
        da = DataAdapter.connect()
        self.assertTrue(os.path.isfile(DataAdapter.prod_database))
        self.assertEqual(da.conn_string, DataAdapter.prod_database)
        da.close()

    def test_connect_to_non_existing_database_throws_error(self):
        self.assertFalse(os.path.isfile('newdb.txt'))
        with self.assertRaises(DatabaseNotFoundError):
            DataAdapter.connect('newdb.txt')

class DataAdapterSecuritiesTests(unittest.TestCase):

    def setUp(self):
        DataAdapter.create_test_database()
        self.database = DataAdapter.connect(DataAdapter.test_database)

    def tearDown(self):
        self.database.close()
        try:
            DataAdapter.delete_test_database()
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
        self.assertEqual(set(expected_tickers), set(tickers))

        # NOTE(steve): try to add an existing ticker
        new_tickers = ['TLS.AX']

        self.database.insert_securities(new_tickers)

        tickers = self.database.get_securities_list()
        self.assertEqual(set(expected_tickers), set(tickers))

    def test_update_equity_data_for_security_not_in_list_raises_error(self):
        ticker = 'AMZN'
        with self.assertRaises(InvalidTickerError):
            self.database.update_market_data(ticker, None)

    @skip
    def test_update_equity_data(self):
        ticker = 'AMZN'
        self.database.insert_securities([ticker])

        dt = datetime.datetime(2019, 8, 27)
        expected_data = get_expected_equity_data()
        self.database.update_market_data(ticker, (dt, expected_data))

        actual_data = self.database.get_equity_data(ticker, dt)
        self.assertEqual(expected_data, actual_data)

    @skip
    def test_get_equity_data_after_multiple_data_updates(self):
        self.fail("NOT IMPLEMENTED")

    @skip
    def test_get_equity_data_for_invalid_ticker_raises_error(self):
        self.fail("NOT IMPLEMENTED")

    @skip
    def test_get_equity_data_for_invalid_date_raises_error(self):
        self.fail("NOT IMPLEMENTED")

class TextDataModelTests(unittest.TestCase):

    def test_equality(self):
        data_1 = TextDataModel()
        data_1.securities = ['AMZN', 'GOOG', 'TLS.AX']
        data_1.equity_data = get_expected_equity_data()

        data_2 = TextDataModel()
        data_2.securities = ['AMZN', 'GOOG', 'TLS.AX']
        data_2.equity_data = get_expected_equity_data()

        self.assertEqual(data_1, data_2)

    def test_to_dict(self):
        data = TextDataModel()
        data.securities = ['AMZN', 'GOOG', 'TLS.AX']
        data.equity_data = get_expected_equity_data()

        dict_data = data.to_dict()

        expected_dict_data = {
            'securities': ['AMZN', 'GOOG', 'TLS.AX'],
            'equity_data': get_expected_equity_data().to_dict()
        }

        self.assertEqual(dict_data, expected_dict_data)

    def test_from_dict(self):
        dict_data = {
            'securities': ['AMZN', 'GOOG', 'TLS.AX'],
            'equity_data': get_expected_equity_data().to_dict()
        }

        expected_data = TextDataModel()
        expected_data.securities = ['AMZN', 'GOOG', 'TLS.AX']
        expected_data.equity_data = get_expected_equity_data()

        actual_data = TextDataModel.from_dict(dict_data)

        self.assertEqual(expected_data, actual_data)

class EquityDataTests(unittest.TestCase):

    def test_to_dict(self):
        data = get_expected_equity_data()
        expected_dict = {
            'open': '1898.00',
            'high': '1903.79',
            'low': '1856.00',
            'close': '1889.98',
            'adj_close': '1889.98',
            'volume': int(5718000)
        }

        actual_dict = data.to_dict()
        self.assertEqual(expected_dict, actual_dict)

    def test_from_dict(self):
        dict_data = {
            'open': '1898.00',
            'high': '1903.79',
            'low': '1856.00',
            'close': '1889.98',
            'adj_close': '1889.98',
            'volume': int(5718000)
        }
        expected_data = get_expected_equity_data()

        actual_data = EquityData.from_dict(dict_data)

        self.assertEqual(expected_data, actual_data)

if __name__ == '__main__':
    unittest.main()
