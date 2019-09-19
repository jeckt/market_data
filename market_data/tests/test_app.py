#!/usr/bin/env python

import os
import sys
import inspect
file_path = os.path.dirname(inspect.getfile(inspect.currentframe()))
sys.path.insert(0, os.path.split(os.path.split(file_path)[0])[0])

import unittest
from unittest.mock import patch
import app
from market_data.data_adapter import DataAdapter

class AppUserInputTests(unittest.TestCase):

    def setUp(self):
        self.database = DataAdapter.test_database

    def tearDown(self):
        DataAdapter.delete_test_database()

    @patch('builtins.print', autospec=True)
    def test_invalid_menu_option_selected(self, mock_print):
        sys.argv = ['./app.py', self.database]
        app.main()

        with patch('builtins.input', autospec=True) as mock_input:
            mock_input.return_value = 4
            running = app.process_user_input()
            mock_input.assert_called_with("Option: ")
            mock_print.assert_called_with(app.INVALID_MENU_OPTION_MSG)
            self.assertTrue(running)

class AppDatabaseTests(unittest.TestCase):

    def setUp(self):
        self.database = 'testdb.json'

    def tearDown(self):
        if os.path.isfile(self.database):
            os.remove(self.database)

    @patch('builtins.print', autospec=True)
    def test_app_terminates_if_no_database_provided(self, mock_print):
        sys.argv = ['./app.py']
        running = app.main()
        mock_print.assert_called_with(app.NO_DATABASE_SPECIFIED_MSG)
        self.assertFalse(running)

    @patch('builtins.print', autospec=True)
    def test_app_creates_database_on_database_not_found(self, mock_print):
        sys.argv = ['./app.py', self.database]

        running = app.main()

        msg = app.get_new_database_created_msg(self.database)
        mock_print.assert_called_with(msg)
        self.assertTrue(os.path.isfile(self.database))
        self.assertTrue(running)

        os.remove(self.database)

    @patch('builtins.print', autospec=True)
    def test_app_loads_existing_database(self, mock_print):
        open(self.database, 'w').close()
        self.assertTrue(os.path.isfile(self.database))
        sys.argv = ['./market_data/app.py', self.database]

        running = app.main()

        msg = app.get_load_existing_database_msg(self.database)
        mock_print.assert_called_with(msg)
        self.assertTrue(running)

        os.remove(self.database)

if __name__ == '__main__':
    unittest.main()
