#!/usr/bin/env python

import os
import sys
import inspect
file_path = os.path.dirname(inspect.getfile(inspect.currentframe()))
sys.path.insert(0, os.path.split(os.path.split(file_path)[0])[0])

import unittest
from unittest.mock import patch

from freezegun import freeze_time

import app
from market_data.data_adapter import DataAdapter
import market_data.tests.utils as test_utils

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

        msg = app.Messages.new_database_created(self.database)
        self.expected_output.append(msg)
        self.expected_output.append(app.Messages.main_menu())
        self.expected_output.append(app.Messages.option_input())

    def tearDown(self):
        try:
            DataAdapter.delete_test_database()
        except:
            pass

    def test_quit_option_selected_exits_app(self):
        self.user_input.append(app.MenuOptions.QUIT)

        sys.argv = ['./app.py', self.database]
        app.main()

        self.expected_output.append(app.Messages.quit())

        check_output(self.actual_output, self.expected_output)

    def test_invalid_menu_option_selected(self):
        self.user_input.append('-1')
        self.user_input.append(app.MenuOptions.QUIT)

        sys.argv = ['./app.py', self.database]
        app.main()

        self.expected_output.append(app.Messages.invalid_option())
        self.expected_output.append(app.Messages.main_menu())
        self.expected_output.append(app.Messages.option_input())
        self.expected_output.append(app.Messages.quit())

        check_output(self.actual_output, self.expected_output)

    def test_add_securities(self):
        self.user_input.append(app.MenuOptions.ADD_SECURITIES)
        self.user_input.append('AMZN')
        self.user_input.append(app.MenuOptions.QUIT)

        sys.argv = ['./app.py', self.database]
        app.main()

        self.expected_output.append(app.Messages.add_security_input())
        self.expected_output.append(app.Messages.security_added('AMZN'))
        self.expected_output.append(app.Messages.main_menu())
        self.expected_output.append(app.Messages.option_input())
        self.expected_output.append(app.Messages.quit())

        check_output(self.actual_output, self.expected_output)

    def test_view_securities(self):
        self.user_input.append(app.MenuOptions.ADD_SECURITIES)
        self.user_input.append('AMZN')
        self.user_input.append(app.MenuOptions.VIEW_SECURITIES)
        self.user_input.append('0') # Return to Main Menu
        self.user_input.append(app.MenuOptions.QUIT)

        sys.argv = ['./app.py', self.database]
        app.main()

        self.expected_output.append(app.Messages.add_security_input())
        self.expected_output.append(app.Messages.security_added('AMZN'))

        self.expected_output.append(app.Messages.main_menu())
        self.expected_output.append(app.Messages.option_input())

        self.expected_output.append(app.Messages.view_securities(['AMZN']))

        self.expected_output.append(app.Messages.option_input())
        self.expected_output.append(app.Messages.main_menu())
        self.expected_output.append(app.Messages.option_input())
        self.expected_output.append(app.Messages.quit())

        check_output(self.actual_output, self.expected_output)

class AppViewSecuritiesTests(unittest.TestCase):
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

        msg = app.Messages.new_database_created(self.database)
        self.expected_output.append(msg)
        self.expected_output.append(app.Messages.main_menu())
        self.expected_output.append(app.Messages.option_input())

    def tearDown(self):
        try:
            DataAdapter.delete_test_database()
        except:
            pass

    @freeze_time('2019-05-10')
    @patch('market_data.scraper.Scraper.scrape_equity_data', autospec=True)
    def test_update_security_data(self, mock_scraper):
        ticker, dt, expected_data = test_utils.get_expected_equity_data()
        mock_scraper.return_value = expected_data

        self.user_input.append(app.MenuOptions.ADD_SECURITIES)
        self.user_input.append(ticker)
        self.user_input.append(app.MenuOptions.UPDATE_MARKET_DATA)
        self.user_input.append(app.MenuOptions.VIEW_SECURITIES)
        self.user_input.append('1') # View AMZN security data
        self.user_input.append('') # Press any key to return to view securities
        self.user_input.append('0') # Return to Main Menu
        self.user_input.append(app.MenuOptions.QUIT)

        sys.argv = ['./app.py', self.database]
        app.main()

        # Add security
        self.expected_output.append(app.Messages.add_security_input())
        self.expected_output.append(app.Messages.security_added(ticker))

        # Update market data
        self.expected_output.append(app.Messages.main_menu())
        self.expected_output.append(app.Messages.option_input())
        self.expected_output.append(app.Messages.market_data_updated())

        # View securities in app
        self.expected_output.append(app.Messages.main_menu())
        self.expected_output.append(app.Messages.option_input())
        self.expected_output.append(app.Messages.view_securities([ticker]))
        self.expected_output.append(app.Messages.option_input())

        # View current security data in app
        self.expected_output.append(app.Messages.view_security_data(ticker,
                                    [(dt, expected_data)]))
        self.expected_output.append(app.Messages.any_key_to_return())
        self.expected_output.append(app.Messages.view_securities([ticker]))
        self.expected_output.append(app.Messages.option_input())

        # Return to main menu and quit app
        self.expected_output.append(app.Messages.main_menu())
        self.expected_output.append(app.Messages.option_input())
        self.expected_output.append(app.Messages.quit())

        check_output(self.actual_output, self.expected_output)

    def test_no_security_data(self):
        self.user_input.append(app.MenuOptions.ADD_SECURITIES)
        self.user_input.append('AMZN')
        self.user_input.append(app.MenuOptions.VIEW_SECURITIES)
        self.user_input.append('1') # View AMZN security data
        self.user_input.append('0') # Return to Main Menu
        self.user_input.append(app.MenuOptions.QUIT)

        sys.argv = ['./app.py', self.database]
        app.main()

        self.expected_output.append(app.Messages.add_security_input())
        self.expected_output.append(app.Messages.security_added('AMZN'))

        self.expected_output.append(app.Messages.main_menu())
        self.expected_output.append(app.Messages.option_input())

        self.expected_output.append(app.Messages.view_securities(['AMZN']))
        self.expected_output.append(app.Messages.option_input())
        self.expected_output.append(app.Messages.no_security_data('AMZN'))
        self.expected_output.append(app.Messages.view_securities(['AMZN']))
        self.expected_output.append(app.Messages.option_input())

        self.expected_output.append(app.Messages.main_menu())
        self.expected_output.append(app.Messages.option_input())
        self.expected_output.append(app.Messages.quit())

        check_output(self.actual_output, self.expected_output)

    def test_no_securities_loaded(self):
        self.user_input.append(app.MenuOptions.VIEW_SECURITIES)
        self.user_input.append('0') # Return to Main Menu
        self.user_input.append(app.MenuOptions.QUIT)

        sys.argv = ['./app.py', self.database]
        app.main()

        self.expected_output.append(app.Messages.view_securities([]))

        self.expected_output.append(app.Messages.option_input())
        self.expected_output.append(app.Messages.main_menu())
        self.expected_output.append(app.Messages.option_input())
        self.expected_output.append(app.Messages.quit())

        check_output(self.actual_output, self.expected_output)

    def test_invalid_option(self):
        self.user_input.append(app.MenuOptions.VIEW_SECURITIES)
        self.user_input.append('invalid option')
        self.user_input.append('0') # Return to Main Menu
        self.user_input.append(app.MenuOptions.QUIT)

        sys.argv = ['./app.py', self.database]
        app.main()

        self.expected_output.append(app.Messages.view_securities([]))
        self.expected_output.append(app.Messages.option_input())
        self.expected_output.append(app.Messages.invalid_option())

        self.expected_output.append(app.Messages.view_securities([]))
        self.expected_output.append(app.Messages.option_input())

        self.expected_output.append(app.Messages.main_menu())
        self.expected_output.append(app.Messages.option_input())
        self.expected_output.append(app.Messages.quit())

        check_output(self.actual_output, self.expected_output)

    def test_invalid_integer_option(self):
        self.user_input.append(app.MenuOptions.VIEW_SECURITIES)
        self.user_input.append('2')
        self.user_input.append('0') # Return to Main Menu
        self.user_input.append(app.MenuOptions.QUIT)

        sys.argv = ['./app.py', self.database]
        app.main()

        self.expected_output.append(app.Messages.view_securities([]))
        self.expected_output.append(app.Messages.option_input())
        self.expected_output.append(app.Messages.invalid_option())

        self.expected_output.append(app.Messages.view_securities([]))
        self.expected_output.append(app.Messages.option_input())

        self.expected_output.append(app.Messages.main_menu())
        self.expected_output.append(app.Messages.option_input())
        self.expected_output.append(app.Messages.quit())

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

        self.expected_output.append(app.Messages.no_database_specified())
        check_output(self.actual_output, self.expected_output)

    def test_app_creates_database_on_database_not_found(self):
        with patch('app.process_user_input', autospec=True) as mock_proc:
            mock_proc.return_value = False
            sys.argv = ['./app.py', self.database]
            app.main()

        msg = app.Messages.new_database_created(self.database)
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

        msg = app.Messages.load_existing_database(self.database)
        self.expected_output.append(msg)
        self.expected_output.append(app.Messages.main_menu())

        check_output(self.actual_output, self.expected_output)

if __name__ == '__main__':
    unittest.main()
