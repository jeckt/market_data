#!/usr/bin/env python

import os
import sys
import inspect
file_path = os.path.dirname(inspect.getfile(inspect.currentframe()))
sys.path.insert(0, os.path.split(os.path.split(file_path)[0])[0])

import unittest
from unittest import skip
from market_data.data_adapter import DataAdapter
from market_data.data_adapter import DatabaseExistsError, DatabaseNotFoundError

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

if __name__ == '__main__':
    unittest.main()
