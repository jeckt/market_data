#!/usr/bin/env python

import os
import sys
import inspect
file_path = os.path.dirname(inspect.getfile(inspect.currentframe()))
sys.path.insert(0, os.path.split(os.path.split(file_path)[0])[0])

import unittest
from unittest.mock import patch
import datetime

from parameterized import parameterized_class
from freezegun import freeze_time

import app
from market_data.market_data import MarketData
import market_data.data_adapter as data_adapter
from market_data.scraper import InvalidDateError, InvalidTickerError
import market_data.tests.utils as test_utils

# NOTE(steve): this is so we don't trigger the clear the console screen
# function which is used for a better user experience
app.TEST_MODE = True

def check_output(actual_output, expected_output):
    for actual, expected in zip(actual_output, expected_output):
        if actual != expected:
            print(f'Actual: {actual}')
            print(f'Expected: {expected}')
        assert actual == expected
    assert len(actual_output) == len(expected_output)

def common_setup(obj):
    obj.da = data_adapter.get_adapter(obj.data_adapter_source)
    obj.database = obj.da.test_database

    app.DATA_ADAPTER_SOURCE = obj.data_adapter_source

    obj.expected_output = []
    obj.actual_output = []
    obj.user_input = []

    def mock_input(s):
        obj.actual_output.append(s)
        if len(obj.user_input) > 0:
            return obj.user_input.pop(0)

    app.input = mock_input
    app.print = lambda s: obj.actual_output.append(s)

def common_teardown(obj):
    try:
        obj.da.delete_test_database()
    except:
        pass

@parameterized_class(('data_adapter_source', ),[
    [data_adapter.DataAdapterSource.JSON, ],
    [data_adapter.DataAdapterSource.SQLITE3, ]
])
class AppMainMenuTests(unittest.TestCase):

    def setUp(self):
        common_setup(self)

        msg = app.Messages.new_database_created(self.database)
        self.expected_output.append(msg)
        self.expected_output.append(app.Messages.main_menu())
        self.expected_output.append(app.Messages.option_input())

    def tearDown(self):
        common_teardown(self)

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

@parameterized_class(('data_adapter_source', ),[
    [data_adapter.DataAdapterSource.JSON, ],
    [data_adapter.DataAdapterSource.SQLITE3, ]
])
class AppUpdateMarketDataTests(unittest.TestCase):
    def setUp(self):
        common_setup(self)

        msg = app.Messages.new_database_created(self.database)
        self.expected_output.append(msg)
        self.expected_output.append(app.Messages.main_menu())
        self.expected_output.append(app.Messages.option_input())

    def tearDown(self):
        common_teardown(self)

    @patch('market_data.scraper.Scraper.scrape_eq_multiple_dates',
           autospec=True)
    def test_update_security_data_on_invalid_ticker(self, mock_scraper):
        ticker = 'AAMZNN'
        mock_scraper.side_effect = InvalidTickerError(ticker)

        self.user_input.append(app.MenuOptions.ADD_SECURITIES)
        self.user_input.append(ticker)
        self.user_input.append(app.MenuOptions.UPDATE_MARKET_DATA)
        self.user_input.append(app.MenuOptions.VIEW_SECURITIES)
        self.user_input.append('1') # View AMZN security data
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
        self.expected_output.append(app.Messages.no_security_data(ticker))
        self.expected_output.append(app.Messages.view_securities([ticker]))
        self.expected_output.append(app.Messages.option_input())

        # Quit
        self.expected_output.append(app.Messages.main_menu())
        self.expected_output.append(app.Messages.option_input())
        self.expected_output.append(app.Messages.quit())

        check_output(self.actual_output, self.expected_output)

        # Check that scraper was called
        mock_scraper.assert_called_once()

    @freeze_time('2019-09-29') # Sunday
    @patch('market_data.scraper.Scraper.scrape_eq_multiple_dates',
           autospec=True)
    def test_update_security_data_on_invalid_date(self, mock_scraper):
        ticker = 'AMZN'
        dt = datetime.datetime.today()
        errors = [InvalidDateError(f'{dt}')]
        mock_scraper.return_value = errors

        self.user_input.append(app.MenuOptions.ADD_SECURITIES)
        self.user_input.append(ticker)
        self.user_input.append(app.MenuOptions.UPDATE_MARKET_DATA)
        self.user_input.append(app.MenuOptions.VIEW_SECURITIES)
        self.user_input.append('1') # View AMZN security data
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
        self.expected_output.append(app.Messages.no_security_data(ticker))
        self.expected_output.append(app.Messages.view_securities([ticker]))
        self.expected_output.append(app.Messages.option_input())

        # Quit
        self.expected_output.append(app.Messages.main_menu())
        self.expected_output.append(app.Messages.option_input())
        self.expected_output.append(app.Messages.quit())

        check_output(self.actual_output, self.expected_output)

        # Check that scraper was called
        mock_scraper.assert_called_once()

    # TODO(steve): isn't this duplication of the functional cli test???
    @freeze_time('2019-08-27')
    @patch('market_data.scraper.Scraper.scrape_eq_multiple_dates',
           autospec=True)
    def test_update_security_data_on_multiple_dates(self, mock_scraper):
        # Load test data
        dataset = test_utils.load_test_data()
        ticker = 'AMZN'
        dt1 = datetime.datetime(2019, 8, 23)
        expected_data_dt1 = test_utils.get_test_data(dataset, ticker, dt1)
        dt2 = datetime.datetime(2019, 8, 26)
        expected_data_dt2 = test_utils.get_test_data(dataset, ticker, dt2)
        dt3 = datetime.datetime(2019, 8, 27)
        expected_data_dt3 = test_utils.get_test_data(dataset, ticker, dt3)
        data_series = [
            (dt3, expected_data_dt3),
            (dt2, expected_data_dt2),
            (dt1, expected_data_dt1)
        ]

        # Create an existing database with data already in the database
        self.da.create_test_database()
        data = self.da.connect(self.database)
        data.insert_securities([ticker])

        data.update_market_data(ticker, (dt1, expected_data_dt1))
        data.close()

        sys.argv = ['./app.py', self.database]
        self.expected_output = []
        self.expected_output.append(
            app.Messages.load_existing_database(self.database)
        )
        self.expected_output.append(app.Messages.main_menu())
        self.expected_output.append(app.Messages.option_input())

        ret_data = [
            (dt2.date(), expected_data_dt2),
            (dt3.date(), expected_data_dt3)
        ]
        mock_scraper.return_value = ret_data, []

        self.user_input.append(app.MenuOptions.UPDATE_MARKET_DATA)
        self.expected_output.append(app.Messages.market_data_updated())
        self.expected_output.append(app.Messages.main_menu())
        self.expected_output.append(app.Messages.option_input())

        self.user_input.append(app.MenuOptions.VIEW_SECURITIES)
        self.expected_output.append(app.Messages.view_securities(['AMZN']))
        self.expected_output.append(app.Messages.option_input())

        self.user_input.append('1')
        self.expected_output.append(
            app.Messages.view_security_data(ticker, data_series)
        )
        self.expected_output.append(app.Messages.any_key_to_return())

        self.user_input.append('')
        self.expected_output.append(app.Messages.view_securities(['AMZN']))
        self.expected_output.append(app.Messages.option_input())
        self.user_input.append('0')
        self.expected_output.append(app.Messages.main_menu())
        self.expected_output.append(app.Messages.option_input())
        self.user_input.append(app.MenuOptions.QUIT)
        self.expected_output.append(app.Messages.quit())

        app.main()

        check_output(self.actual_output, self.expected_output)

        # Check that scraper was called
        mock_scraper.assert_called_once()

    @freeze_time('2019-05-10')
    @patch('market_data.scraper.Scraper.scrape_eq_multiple_dates',
           autospec=True)
    def test_update_security_data(self, mock_scraper):
        ticker, dt, expected_data = test_utils.get_expected_equity_data()
        mock_scraper.return_value = [(dt.date(), expected_data)], []

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

        # Check that scraper was called
        mock_scraper.assert_called_once()

@parameterized_class(('data_adapter_source', ),[
    [data_adapter.DataAdapterSource.JSON, ],
    [data_adapter.DataAdapterSource.SQLITE3, ]
])
class AppViewSecuritiesTests(unittest.TestCase):
    def setUp(self):
        common_setup(self)

        msg = app.Messages.new_database_created(self.database)
        self.expected_output.append(msg)
        self.expected_output.append(app.Messages.main_menu())
        self.expected_output.append(app.Messages.option_input())

    def tearDown(self):
        common_teardown(self)

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

@parameterized_class(('data_adapter_source', ),[
    [data_adapter.DataAdapterSource.JSON, ],
    [data_adapter.DataAdapterSource.SQLITE3, ]
])
class AppDatabaseTests(unittest.TestCase):

    def setUp(self):
        app.DATA_ADAPTER_SOURCE = self.data_adapter_source

        if self.data_adapter_source == data_adapter.DataAdapterSource.JSON:
            self.database = 'testdb.json'
        else:
            self.database = 'test.db'

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
