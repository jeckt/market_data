#!/usr/bin/env python

import os
import sys
import inspect
file_path = os.path.dirname(inspect.getfile(inspect.currentframe()))
sys.path.insert(0, os.path.split(os.path.split(file_path)[0])[0])

import unittest
from unittest import skip
import datetime
import json
from market_data.data_adapter import DataAdapter, TextDataModel
from market_data.data_adapter import DatabaseExistsError, DatabaseNotFoundError
from market_data.data import EquityData, InvalidTickerError, InvalidDateError
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

    def test_insert_duplicate_security_does_not_erase_existing_data(self):
        ticker = 'AMZN'
        self.database.insert_securities([ticker])

        with open('market_data/tests/test_data.json', 'r') as db:
            test_data = json.load(db)

        dict_data = test_data[ticker]['27-Aug-2019']
        expected_data = EquityData(
            open=dict_data['open'],
            high=dict_data['high'],
            low=dict_data['low'],
            close=dict_data['close'],
            adj_close=dict_data['adj_close'],
            volume=dict_data['volume']
        )
        dt = datetime.datetime(2019, 8, 27)
        self.database.update_market_data(ticker, (dt, expected_data))

        actual_data = self.database.get_equity_data(ticker, dt)
        self.assertEqual(expected_data, actual_data)

        self.database.insert_securities([ticker])

        actual_data = self.database.get_equity_data(ticker, dt)
        self.assertEqual(expected_data, actual_data)

    def test_update_equity_data(self):
        ticker, dt, expected_data = get_expected_equity_data()
        self.database.insert_securities([ticker])

        self.database.update_market_data(ticker, (dt, expected_data))

        actual_data = self.database.get_equity_data(ticker, dt)
        self.assertEqual(expected_data, actual_data)

    # TODO(steve): check if this a duplication of the test in
    # test_market_data.py. Very similar set up and tests???
    def test_get_equity_data_after_multiple_dates_updates(self):
        ticker = 'AMZN'
        self.database.insert_securities([ticker])

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
        dt_1 = datetime.datetime(2019, 8, 27)
        self.database.update_market_data(ticker, (dt_1, expected_data_1))

        dict_data = test_data[ticker]['26-Aug-2019']
        expected_data_2 = EquityData(
            open=dict_data['open'],
            high=dict_data['high'],
            low=dict_data['low'],
            close=dict_data['close'],
            adj_close=dict_data['adj_close'],
            volume=dict_data['volume']
        )
        dt_2 = datetime.datetime(2019, 8, 26)
        self.database.update_market_data(ticker, (dt_2, expected_data_2))

        actual_data_2 = self.database.get_equity_data(ticker, dt_2)
        self.assertEqual(expected_data_2, actual_data_2)

        actual_data_1 = self.database.get_equity_data(ticker, dt_1)
        self.assertEqual(expected_data_1, actual_data_1)

    def test_get_equity_data_for_multiple_securities(self):
        self.database.insert_securities(['AMZN', 'GOOG'])
        dt = datetime.datetime(2019, 8, 27)

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
        self.database.update_market_data('AMZN', (dt, expected_data_1))

        dict_data = test_data['GOOG']['27-Aug-2019']
        expected_data_2 = EquityData(
            open=dict_data['open'],
            high=dict_data['high'],
            low=dict_data['low'],
            close=dict_data['close'],
            adj_close=dict_data['adj_close'],
            volume=dict_data['volume']
        )
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

class TextDataModelTests(unittest.TestCase):

    def test_equality(self):
        dt = datetime.datetime(2019, 8, 27).strftime('%d-%b-%Y')
        _, _, equity_data = get_expected_equity_data()

        data_1 = TextDataModel()
        data_1.securities = ['AMZN', 'GOOG', 'TLS.AX']
        data_1.equity_data = {
            'AMZN': { dt : equity_data }
        }

        data_2 = TextDataModel()
        data_2.securities = ['AMZN', 'GOOG', 'TLS.AX']
        data_2.equity_data = {
            'AMZN': { dt : equity_data }
        }

        self.assertEqual(data_1, data_2)

    def test_json_encoder_can_serialise_text_data_model(self):
        # set up
        dt = datetime.datetime(2019, 8, 27).strftime('%d-%b-%Y')
        _, _, equity_data = get_expected_equity_data()

        data = TextDataModel()
        data.securities = ['AMZN', 'GOOG', 'TLS.AX']
        data.equity_data = {
            'AMZN': { dt: equity_data }
        }

        # method
        actual_data = json.dumps(data, default=TextDataModel.json_encoder)

        # expected output
        data_dict = {
            "securities": ['AMZN', 'GOOG', 'TLS.AX'],
            'AMZN': {
                dt: {
                    'open': '1898.00',
                    'high': '1903.79',
                    'low': '1856.00',
                    'close': '1889.98',
                    'adj_close': '1889.98',
                    'volume': int(5718000)
                }
            }
        }
        json_data = json.dumps(data_dict)

        # test
        self.assertEqual(json_data, actual_data)

    def test_json_decoder_can_deserialise_text_data_model(self):
        # set up
        dt = datetime.datetime(2019, 8, 27).strftime('%d-%b-%Y')
        data_dict = {
            "securities": ['AMZN', 'GOOG', 'TLS.AX'],
            'AMZN': {
                dt: {
                    'open': '1898.00',
                    'high': '1903.79',
                    'low': '1856.00',
                    'close': '1889.98',
                    'adj_close': '1889.98',
                    'volume': int(5718000)
                }
            }
        }
        json_data = json.dumps(data_dict)

        # method
        actual_data = json.loads(json_data,
                                 object_hook=TextDataModel.json_decoder)

        # expected output
        _, _, equity_data = get_expected_equity_data()
        expected_data = TextDataModel()
        expected_data.securities = ['AMZN', 'GOOG', 'TLS.AX']
        expected_data.equity_data = {
            "AMZN": { dt: equity_data }
        }

        # test
        self.assertEqual(expected_data, actual_data)

if __name__ == '__main__':
    unittest.main()
