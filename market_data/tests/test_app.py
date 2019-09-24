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

def check_output(actual_output, expected_output):
    for actual, expected in zip(actual_output, expected_output):
        if actual != expected:
            print(f'Actual: {actual}')
            print(f'Expected: {expected}')
        assert actual == expected
    assert len(actual_output) == len(expected_output)

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
        self.expected_output.append(app.Messages.main_menu())
        self.expected_output.append(app.USER_OPTION_INPUT)

    def tearDown(self):
        try:
            DataAdapter.delete_test_database()
        except:
            pass

    def test_quit_option_selected_exits_app(self):
        self.user_input.append(app.MenuOptions.QUIT)

        sys.argv = ['./app.py', self.database]
        app.main()

        self.expected_output.append(app.QUIT_MSG)

        check_output(self.actual_output, self.expected_output)

    def test_invalid_menu_option_selected(self):
        self.user_input.append('-1')
        self.user_input.append(app.MenuOptions.QUIT)

        sys.argv = ['./app.py', self.database]
        app.main()

        self.expected_output.append(app.INVALID_MENU_OPTION_MSG)
        self.expected_output.append(app.Messages.main_menu())
        self.expected_output.append(app.USER_OPTION_INPUT)
        self.expected_output.append(app.QUIT_MSG)

        check_output(self.actual_output, self.expected_output)

    def test_view_securities_with_no_securities_loaded(self):
        self.user_input.append(app.MenuOptions.VIEW_SECURITIES)
        self.user_input.append(app.MenuOptions.QUIT)

        sys.argv = ['./app.py', self.database]
        app.main()

        mock_method = 'market_data.market_data.MarketData.get_securities_list'
        with patch(mock_method, autospec=True) as mock_tickers:
            mock_tickers.return_value = []
            self.expected_output.append(app.get_view_securities_msg())

        self.expected_output.append(app.Messages.main_menu())
        self.expected_output.append(app.USER_OPTION_INPUT)
        self.expected_output.append(app.QUIT_MSG)

        check_output(self.actual_output, self.expected_output)

    def test_add_securities(self):
        self.user_input.append(app.MenuOptions.ADD_SECURITIES)
        self.user_input.append('AMZN')
        self.user_input.append(app.MenuOptions.QUIT)

        sys.argv = ['./app.py', self.database]
        app.main()

        self.expected_output.append(app.ADD_SECURITY_INPUT)
        self.expected_output.append(app.get_security_added_msg('AMZN'))
        self.expected_output.append(app.Messages.main_menu())
        self.expected_output.append(app.USER_OPTION_INPUT)
        self.expected_output.append(app.QUIT_MSG)

        check_output(self.actual_output, self.expected_output)

    def test_view_securities(self):
        self.user_input.append(app.MenuOptions.ADD_SECURITIES)
        self.user_input.append('AMZN')
        self.user_input.append(app.MenuOptions.VIEW_SECURITIES)
        self.user_input.append(app.MenuOptions.QUIT)

        sys.argv = ['./app.py', self.database]
        app.main()

        self.expected_output.append(app.ADD_SECURITY_INPUT)
        self.expected_output.append(app.get_security_added_msg('AMZN'))

        self.expected_output.append(app.Messages.main_menu())
        self.expected_output.append(app.USER_OPTION_INPUT)

        mock_method = 'market_data.market_data.MarketData.get_securities_list'
        with patch(mock_method, autospec=True) as mock_tickers:
            mock_tickers.return_value = ['AMZN']
            self.expected_output.append(app.get_view_securities_msg())

        self.expected_output.append(app.Messages.main_menu())
        self.expected_output.append(app.USER_OPTION_INPUT)
        self.expected_output.append(app.QUIT_MSG)

        check_output(self.actual_output, self.expected_output)



class AppDatabaseTests(unittest.TestCase):

    def setUp(self):
        self.database = 'testdb.json'
        self.actual_output = []
        self.expected_output = []
        app.print = lambda s: self.actual_output.append(s)

    def tearDown(self):
        if os.path.isfile(self.database):
            os.remove(self.database)

    def test_app_terminates_if_no_database_provided(self):
        sys.argv = ['./app.py']
        app.main()

        self.expected_output.append(app.NO_DATABASE_SPECIFIED_MSG)
        check_output(self.actual_output, self.expected_output)

    def test_app_creates_database_on_database_not_found(self):
        with patch('app.process_user_input', autospec=True) as mock_proc:
            mock_proc.return_value = False
            sys.argv = ['./app.py', self.database]
            app.main()

        msg = app.get_new_database_created_msg(self.database)
        self.expected_output.append(msg)
        self.expected_output.append(app.Messages.main_menu())

        check_output(self.actual_output, self.expected_output)
        self.assertTrue(os.path.isfile(self.database))

    @patch('builtins.print', autospec=True)
    def test_app_loads_existing_database(self, mock_print):
        open(self.database, 'w').close()
        self.assertTrue(os.path.isfile(self.database))

        with patch('app.process_user_input', autospec=True) as mock_proc:
            mock_proc.return_value = False
            sys.argv = ['./app.py', self.database]
            app.main()

        msg = app.get_load_existing_database_msg(self.database)
        self.expected_output.append(msg)
        self.expected_output.append(app.Messages.main_menu())

        check_output(self.actual_output, self.expected_output)

if __name__ == '__main__':
    unittest.main()
