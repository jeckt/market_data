#!/usr/bin/env python

import os
import sys
import inspect
file_path = os.path.dirname(inspect.getfile(inspect.currentframe()))
sys.path.insert(0, os.path.split(os.path.split(file_path)[0])[0])

import unittest
from unittest import skip
from market_data.data_adaptor import DataAdaptor
from market_data.data_adaptor import DatabaseExistsError, DatabaseNotFoundError

class DataAdaptorTestDatabaseTests(unittest.TestCase):

    def tearDown(self):
        # NOTE(steve): I think it is acceptable to suppress
        # the error here as we only want to make sure the 
        # database is removed after each test and at the
        # same time we want to abstract the implementation
        try:
            DataAdaptor.delete_test_database()
        except:
            pass

    def test_create_test_database(self):
        self.assertFalse(os.path.isfile(DataAdaptor.test_database))
        DataAdaptor.create_test_database()
        self.assertTrue(os.path.isfile(DataAdaptor.test_database))

    def test_delete_test_database(self):
        DataAdaptor.create_test_database()
        self.assertTrue(os.path.isfile(DataAdaptor.test_database))
        DataAdaptor.delete_test_database()
        self.assertFalse(os.path.isfile(DataAdaptor.test_database))

    def test_create_existing_test_database_raises_error(self):
        DataAdaptor.create_test_database()
        with self.assertRaises(DatabaseExistsError):
            DataAdaptor.create_test_database()

    def test_delete_non_existing_test_database_raises_error(self):
        self.assertFalse(os.path.isfile(DataAdaptor.test_database))
        with self.assertRaises(DatabaseNotFoundError):
            DataAdaptor.delete_test_database()

if __name__ == '__main__':
    unittest.main()
