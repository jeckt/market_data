#!/usr/bin/env python

import unittest
from unittest.mock import patch
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
        # NOTE(steve): we patch the process user input function here
        # so that we can control the loop later in the test otherwise
        # we would not be able to test the changes in user input requests
        expected_output, actual_output = [], []
        user_input = []

        # Upon providing the database connection string he is able 
        # to move on to the next screen in the app.
        expected_output.append(app.get_new_database_created_msg(self.database))

        # Curious to see if there are any securities in the app already
        # he select option 1 to view the securities.
        user_input.append('1')
        expected_output.append('Option: ')

        msg = """
        Currently no securities have been added to database.

        """
        msg += app.MENU_OPTIONS
        expected_output.append(msg)

        # As expected there are no securities so he proceeds to option
        # 2 to add securities
        user_input.append('2')
        expected_output.append('Option: ')

        # He adds AMZN to the database
        user_input.append('AMZN')
        msg = """
        Please type in the Yahoo ticker for the security you want to add:
        """
        expected_output.append(msg)

        msg = """
        AMZN has been added.

        """
        expected_output.append(msg)

        # He is then asked if he would like to add another security. 
        # Happy with just adding he selects 'n'
        user_input.append('n')
        msg = """
        Would you please to add another security? [y/n]:
        """
        expected_output.append(msg)

        msg = app.MENU_OPTIONS
        expected_output.append(msg)

        # He now checks that the security has been added to the list
        user_input.append('1')
        expected_output.append('Option: ')

        msg = """
        The following securities are in the database:

            1. AMZN

        """
        msg += app.MENU_OPTIONS
        expected_output.append(msg)

        # Satisfied with the results he closes the application
        user_input.append('3')
        expected_output.append('Option: ')

        msg = """
        Thank you for using the Market Data Application. Bye!
        """
        expected_output.append(msg)

        # Method
        sys.argv = ['./app.py', self.database]
        app.main()

        # Tests
        self.assertEqual(len(actual_output), len(expected_output))
        for actual, expected in zip(actual_output, expected_output):
            self.assertEqual(actual, expected)

if __name__ == '__main__':
    unittest.main()
