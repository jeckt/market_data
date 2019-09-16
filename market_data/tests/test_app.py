#!/usr/bin/env python

import os
import sys
import inspect
file_path = os.path.dirname(inspect.getfile(inspect.currentframe()))
sys.path.insert(0, os.path.split(os.path.split(file_path)[0])[0])

import unittest
from unittest.mock import patch
import market_data.app as app

class AppTests(unittest.TestCase):

    def setUp(self):
        self.database = 'testdb.json'

    def tearDown(self):
        if os.path.isfile(self.database):
            os.remove(self.database)

    @patch('builtins.print', autospec=True)
    def test_app_terminates_if_no_database_provided(self, mock_print):
        sys.argv = ['./market_data/app.py']
        app.main()
        mock_print.assert_called_with(app.NO_DATABASE_SPECIFIED_MSG)

    @patch('builtins.print', autospec=True)
    def test_app_creates_database_on_database_not_found(self, mock_print):
        sys.argv = ['./market_data/app.py', self.database]

        app.main()

        msg = app.get_new_database_created_msg(self.database)
        mock_print.assert_called_with(msg)
        self.assertTrue(os.path.isfile(db))

        os.remove(db)

    @patch('builtins.print', autospec=True)
    def test_app_loads_existing_database(self, mock_print):
        db = 'testdb.json'
        open(db, 'w').close()
        self.assertTrue(os.path.isfile(db))
        sys.argv = ['./market_data/app.py', db]

        app.main()

        msg = app.get_load_existing_database_msg(self.database)
        mock_print.assert_called_with(msg)

        os.remove(db)

if __name__ == '__main__':
    unittest.main()
