#!/usr/bin/env python

import unittest
import sys
import app
from market_data.data_adapter import DataAdapter

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
        expected_output.append(app.VIEW_NO_SECURITIES)
        expected_output.append(app.MENU_OPTIONS)
        expected_output.append(app.USER_OPTION_INPUT)

        # As expected there are no securities so he proceeds to option
        # 2 to add securities
        user_input.append('2')
        msg = """
        Please type in the Yahoo ticker for the security you want to add:
        """
        expected_output.append(msg)

        # He adds AMZN to the database
        user_input.append('AMZN')
        msg = 'AMZN has been added'
        expected_output.append(msg)
        msg = 'Would you please to add another security? [y/n]: '
        expected_output.append(msg)

        # He is then asked if he would like to add another security. 
        # Happy with just adding he selects 'n'
        user_input.append('n')
        expected_output.append(app.MENU_OPTIONS)
        expected_output.append(app.USER_OPTION_INPUT)

        # He now checks that the security has been added to the list
        user_input.append(app.VIEW_NO_SECURITIES)
        msg = """
        The following securities are in the database:

            1. AMZN

        """
        expected_output.append(msg)
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
