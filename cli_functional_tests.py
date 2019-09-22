#!/usr/bin/env python

import unittest
from unittest.mock import patch
import sys
import app
from market_data.data_adapter import DataAdapter

# TODO(steve): we need to rethink how we expose the app messages,
# options and methods to users (even in testing!!!)
class CommandLineInterfaceTests(unittest.TestCase):

    def setUp(self):
        self.database = DataAdapter.test_database

    def tearDown(self):
        DataAdapter.delete_test_database()

    def test_add_securities_and_view_securities(self):
        expected_output, actual_output = [], []
        # Alex has heard about this new command line app that can
        # store financial market data for him. He decides to open it
        # NOTE(steve): simulates ./app.py call on command line
        expected_output.append(app.NO_DATABASE_SPECIFIED_MSG)
        def mock_input(s):
            actual_output.append(s)
            return user_input.pop(0)

        app.input = mock_input
        app.print = lambda s: actual_output.append(s)

        app.main()

        # Upon opening it, he is told that he has not specified
        # a database for the application to hook up to.
        self.assertEqual(expected_output, actual_output)

        # Reading through the help provided, Alex decides to give it another
        # go and this time provides a database connection for the app to
        # create a new database file
        sys.argv = ['./app.py', self.database]
        expected_output, actual_output = [], []
        user_input = []

        # Upon providing the database connection string he is able 
        # to move on to the next screen in the app.
        expected_output.append(app.get_new_database_created_msg(self.database))
        expected_output.append(app.MENU_OPTIONS)
        expected_output.append(app.USER_OPTION_INPUT)

        # Curious to see if there are any securities in the app already
        # he selects option 1 to view the securities.
        user_input.append(app.VIEW_SECURITIES_OPTION)
        mock_method = 'market_data.market_data.MarketData.get_securities_list'
        with patch(mock_method, autospec=True) as mock_tickers:
            mock_tickers.return_value = []
            expected_output.append(app.get_view_securities_msg())
        expected_output.append(app.MENU_OPTIONS)
        expected_output.append(app.USER_OPTION_INPUT)

        # As expected there are no securities so he proceeds to option
        # 2 to add securities
        user_input.append(app.ADD_SECURITIES_OPTION)
        expected_output.append(app.ADD_SECURITY_INPUT)

        # He adds AMZN to the database
        user_input.append('AMZN')
        expected_output.append(app.get_security_added_msg('AMZN'))
        expected_output.append(app.MENU_OPTIONS)
        expected_output.append(app.USER_OPTION_INPUT)

        # He now checks that the security has been added to the list
        user_input.append(app.VIEW_SECURITIES_OPTION)
        mock_method = 'market_data.market_data.MarketData.get_securities_list'
        with patch(mock_method, autospec=True) as mock_tickers:
            mock_tickers.return_value = ['AMZN']
            expected_output.append(app.get_view_securities_msg())
        expected_output.append(app.MENU_OPTIONS)
        expected_output.append(app.USER_OPTION_INPUT)

        # Satisfied with the results he closes the application
        user_input.append(app.QUIT_OPTION)
        expected_output.append(app.QUIT_MSG)

        # Method
        app.main()

        # Tests
        for actual, expected in zip(actual_output, expected_output):
            self.assertEqual(actual, expected)
        self.assertEqual(len(actual_output), len(expected_output))

if __name__ == '__main__':
    unittest.main()
