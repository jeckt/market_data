#!/usr/bin/env python

import sys
import unittest
from unittest.mock import patch

from freezegun import freeze_time

import app
from market_data.data_adapter import DataAdapter
import market_data.tests.utils as test_utils

# TODO(steve): we need to rethink how we expose the app messages,
# options and methods to users (even in testing!!!)
class CommandLineInterfaceTests(unittest.TestCase):

    def setUp(self):
        self.database = DataAdapter.test_database
        self.actual_output = []
        self.user_input = []
        def mock_input(s):
            self.actual_output.append(s)
            return self.user_input.pop(0)

        app.input = mock_input
        app.print = lambda s: self.actual_output.append(s)

    def tearDown(self):
        try:
            DataAdapter.delete_test_database()
        except:
            pass

    @freeze_time('2019-05-10')
    @patch('market_data.scraper.Scraper.scrape_equity_data', autospec=True)
    def test_update_and_view_updated_security(self, mock_scraper):
        ticker, dt, expected_data = test_utils.get_expected_equity_data()
        mock_scraper.return_value = expected_data

        # Mary on hearing from Alex about this new command line
        # app decides to try it.
        sys.argv = ['./app.py', self.database]
        expected_output = []

        # Upon opening the app she is presented with a bunch of options
        expected_output.append(app.Messages.new_database_created(self.database))
        expected_output.append(app.Messages.main_menu())
        expected_output.append(app.Messages.option_input())

        # She selects to add a security and adds 'AMZN'
        # The app then returns her to the main menu.
        self.user_input.append(app.MenuOptions.ADD_SECURITIES)
        expected_output.append(app.Messages.add_security_input())
        self.user_input.append('AMZN')
        expected_output.append(app.Messages.security_added('AMZN'))
        expected_output.append(app.Messages.main_menu())
        expected_output.append(app.Messages.option_input())

        # Since the US equities market is closed she decides
        # to update the market data whcih will update the 
        # security she just added
        # TODO(steve) we need to mock the update market data call so
        # that it returns the exact market data we expect.
        self.user_input.append(app.MenuOptions.UPDATE_MARKET_DATA)
        expected_output.append(app.Messages.market_data_updated())
        expected_output.append(app.Messages.main_menu())
        expected_output.append(app.Messages.option_input())

        # She then proceeds to view the updated market data
        self.user_input.append(app.MenuOptions.VIEW_SECURITIES)
        expected_output.append(app.Messages.view_securities(['AMZN']))
        expected_output.append(app.Messages.option_input())

        # She then chooses to see the updated market data in AMZN
        self.user_input.append('1')
        expected_output.append(app.Messages.view_security_data(ticker,
                                    [(dt, expected_data)]))
        expected_output.append(app.Messages.any_key_to_return())

        # Happy with the results she returns the view securities page
        self.user_input.append('')
        mock_method = 'market_data.market_data.MarketData.get_securities_list'
        expected_output.append(app.Messages.view_securities(['AMZN']))
        expected_output.append(app.Messages.option_input())

        # This time she selects to go back to the main menu
        # and quits the application
        self.user_input.append('0')
        expected_output.append(app.Messages.main_menu())
        expected_output.append(app.Messages.option_input())
        self.user_input.append(app.MenuOptions.QUIT)
        expected_output.append(app.Messages.quit())

        # Method
        app.main()

        # Tests
        for actual, expected in zip(self.actual_output, expected_output):
            self.assertEqual(actual, expected)
        self.assertEqual(len(self.actual_output), len(expected_output))

    def test_add_securities_and_view_securities(self):
        expected_output = []
        # Alex has heard about this new command line app that can
        # store financial market data for him. He decides to open it
        # NOTE(steve): simulates ./app.py call on command line
        expected_output.append(app.Messages.no_database_specified())
        app.main()

        # Upon opening it, he is told that he has not specified
        # a database for the application to hook up to.
        self.assertEqual(expected_output, self.actual_output)

        # Reading through the help provided, Alex decides to give it another
        # go and this time provides a database connection for the app to
        # create a new database file
        sys.argv = ['./app.py', self.database]
        expected_output = []
        self.actual_output = []

        # Upon providing the database connection string he is able 
        # to move on to the next screen in the app.
        expected_output.append(app.Messages.new_database_created(self.database))
        expected_output.append(app.Messages.main_menu())
        expected_output.append(app.Messages.option_input())

        # Curious to see if there are any securities in the app already
        # he selects option 1 to view the securities.
        self.user_input.append(app.MenuOptions.VIEW_SECURITIES)
        expected_output.append(app.Messages.view_securities([]))
        expected_output.append(app.Messages.option_input())

        # As expected there are no securities so he returns to the main menu
        # and proceeds to option 2 to add securities
        self.user_input.append('0')
        expected_output.append(app.Messages.main_menu())
        expected_output.append(app.Messages.option_input())

        self.user_input.append(app.MenuOptions.ADD_SECURITIES)
        expected_output.append(app.Messages.add_security_input())

        # He adds AMZN to the database
        self.user_input.append('AMZN')
        expected_output.append(app.Messages.security_added('AMZN'))
        expected_output.append(app.Messages.main_menu())
        expected_output.append(app.Messages.option_input())

        # He now checks that the security has been added to the list
        self.user_input.append(app.MenuOptions.VIEW_SECURITIES)
        expected_output.append(app.Messages.view_securities(['AMZN']))
        expected_output.append(app.Messages.option_input())

        # Satisfied with the results he returns to the main menu
        # and closes the application
        self.user_input.append('0')
        expected_output.append(app.Messages.main_menu())
        expected_output.append(app.Messages.option_input())
        self.user_input.append(app.MenuOptions.QUIT)
        expected_output.append(app.Messages.quit())

        # Method
        app.main()

        # Tests
        for actual, expected in zip(self.actual_output, expected_output):
            self.assertEqual(actual, expected)
        self.assertEqual(len(self.actual_output), len(expected_output))

if __name__ == '__main__':
    unittest.main()
