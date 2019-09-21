#!/usr/bin/env python

import os
import sys
import inspect
file_path = os.path.dirname(inspect.getfile(inspect.currentframe()))
sys.path.insert(0, os.path.split(os.path.split(file_path)[0])[0])

import unittest
from unittest import skip
from unittest.mock import patch
import app
from market_data.data_adapter import DataAdapter

class AppMainMenuTests(unittest.TestCase):

    def setUp(self):
        self.database = DataAdapter.test_database

        self.expected_output = []
        self.actual_output = []
        self.user_input = []

        def mock_input(s):
            self.actual_output.append(s)
            if len(self.user_input) > 0:
                return self.user_input.pop(0)

        app.input = mock_input
        app.print = lambda s: self.actual_output.append(s)

        msg = app.get_new_database_created_msg(self.database)
        self.expected_output.append(msg)
        self.expected_output.append(app.USER_OPTION_INPUT)

    def tearDown(self):
        try:
            DataAdapter.delete_test_database()
        except:
            pass

    def check_output(self):
        for actual, expected in zip(self.actual_output, self.expected_output):
            self.assertEqual(actual, expected)
        self.assertEqual(len(self.actual_output), len(self.expected_output))

    def test_quit_option_selected_exits_app(self):
        self.user_input.append(app.QUIT_OPTION)

        sys.argv = ['./app.py', self.database]
        app.main()

        self.expected_output.append(app.QUIT_MSG)

        self.check_output()

    def test_invalid_menu_option_selected(self):
        self.user_input.append('-1')
        self.user_input.append(app.QUIT_OPTION)

        sys.argv = ['./app.py', self.database]
        app.main()

        self.expected_output.append(app.INVALID_MENU_OPTION_MSG)
        self.expected_output.append(app.USER_OPTION_INPUT)
        self.expected_output.append(app.QUIT_MSG)

        self.check_output()

    def test_view_securities_with_no_securities_loaded(self):
        self.user_input.append(app.VIEW_SECURITIES_OPTION)
        self.user_input.append(app.QUIT_OPTION)

        sys.argv = ['./app.py', self.database]
        app.main()

        self.expected_output.append(app.VIEW_NO_SECURITIES)
        self.expected_output.append(app.USER_OPTION_INPUT)
        self.expected_output.append(app.QUIT_MSG)

        self.check_output()

class AppDatabaseTests(unittest.TestCase):

    def setUp(self):
        self.database = 'testdb.json'

    def tearDown(self):
        if os.path.isfile(self.database):
            os.remove(self.database)

    @patch('builtins.print', autospec=True)
    def test_app_terminates_if_no_database_provided(self, mock_print):
        sys.argv = ['./app.py']
        app.main()
        mock_print.assert_called_with(app.NO_DATABASE_SPECIFIED_MSG)

    @patch('builtins.print', autospec=True)
    def test_app_creates_database_on_database_not_found(self, mock_print):
        with patch('app.process_user_input', autospec=True) as mock_proc:
            mock_proc.return_value = False
            sys.argv = ['./app.py', self.database]
            app.main()

        msg = app.get_new_database_created_msg(self.database)
        mock_print.assert_called_with(msg)
        self.assertTrue(os.path.isfile(self.database))

        os.remove(self.database)

    @patch('builtins.print', autospec=True)
    def test_app_loads_existing_database(self, mock_print):
        open(self.database, 'w').close()
        self.assertTrue(os.path.isfile(self.database))

        with patch('app.process_user_input', autospec=True) as mock_proc:
            mock_proc.return_value = False
            sys.argv = ['./app.py', self.database]
            app.main()

        msg = app.get_load_existing_database_msg(self.database)
        mock_print.assert_called_with(msg)

        os.remove(self.database)

if __name__ == '__main__':
    unittest.main()
