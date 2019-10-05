#!/usr/bin/env python

import sys
import unittest
from unittest.mock import patch
import datetime

from freezegun import freeze_time

import app
from app import Messages as msg
import market_data.data_adapter as data_adapter
import market_data.tests.utils as test_utils

# TODO(steve): we need to rethink how we expose the app messages,
# options and methods to users (even in testing!!!)
class CommandLineInterfaceTests(unittest.TestCase):

    def setUp(self):
        self.da = data_adapter.get_adapter(data_adapter.DataAdapterSource.JSON)
        self.database = self.da.test_database
        self.actual_output = []
        self.user_input = []
        def mock_input(s):
            self.actual_output.append(s)
            return self.user_input.pop(0)

        app.input = mock_input
        app.print = lambda s: self.actual_output.append(s)

    def tearDown(self):
        try:
            self.da.delete_test_database()
        except:
            pass

    @freeze_time('2019-08-27')
    @patch('market_data.scraper.Scraper.scrape_equity_data', autospec=True)
    def test_update_security_for_multiple_dates(self, mock_scraper):
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

        # Adam opens the app on an existing database.
        sys.argv = ['./app.py', self.database]
        expected_output = []

        # He gets the standard main menu options to start
        expected_output.append(msg.load_existing_database(self.database))
        expected_output.append(msg.main_menu())
        expected_output.append(msg.option_input())

        # He updates the market data to get the latest data available
        # The app will update all market data from the last available
        # date to the current date
        mock_scraper.side_effect = [expected_data_dt2, expected_data_dt3]
        self.user_input.append(app.MenuOptions.UPDATE_MARKET_DATA)
        expected_output.append(msg.market_data_updated())
        expected_output.append(msg.main_menu())
        expected_output.append(msg.option_input())

        # He then proceeds to view the updated market data
        self.user_input.append(app.MenuOptions.VIEW_SECURITIES)
        expected_output.append(msg.view_securities(['AMZN']))
        expected_output.append(msg.option_input())

        # He then chooses to see the updated market data in AMZN
        self.user_input.append('1')
        expected_output.append(msg.view_security_data(ticker, data_series))
        expected_output.append(msg.any_key_to_return())

        # Happy with the results he returns the view securities page
        self.user_input.append('')
        expected_output.append(msg.view_securities(['AMZN']))
        expected_output.append(msg.option_input())

        # This time she selects to go back to the main menu
        # and quits the application
        self.user_input.append('0')
        expected_output.append(msg.main_menu())
        expected_output.append(msg.option_input())
        self.user_input.append(app.MenuOptions.QUIT)
        expected_output.append(msg.quit())

        # Method
        app.main()

        # Tests
        for actual, expected in zip(self.actual_output, expected_output):
            self.assertEqual(actual, expected)
        self.assertEqual(len(self.actual_output), len(expected_output))

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
        expected_output.append(msg.new_database_created(self.database))
        expected_output.append(msg.main_menu())
        expected_output.append(msg.option_input())

        # She selects to add a security and adds 'AMZN'
        # The app then returns her to the main menu.
        self.user_input.append(app.MenuOptions.ADD_SECURITIES)
        expected_output.append(msg.add_security_input())
        self.user_input.append('AMZN')
        expected_output.append(msg.security_added('AMZN'))
        expected_output.append(msg.main_menu())
        expected_output.append(msg.option_input())

        # Since the US equities market is closed she decides
        # to update the market data whcih will update the 
        # security she just added
        self.user_input.append(app.MenuOptions.UPDATE_MARKET_DATA)
        expected_output.append(msg.market_data_updated())
        expected_output.append(msg.main_menu())
        expected_output.append(msg.option_input())

        # She then proceeds to view the updated market data
        self.user_input.append(app.MenuOptions.VIEW_SECURITIES)
        expected_output.append(msg.view_securities(['AMZN']))
        expected_output.append(msg.option_input())

        # She then chooses to see the updated market data in AMZN
        self.user_input.append('1')
        expected_output.append(msg.view_security_data(ticker,
                                    [(dt, expected_data)]))
        expected_output.append(msg.any_key_to_return())

        # Happy with the results she returns the view securities page
        self.user_input.append('')
        expected_output.append(msg.view_securities(['AMZN']))
        expected_output.append(msg.option_input())

        # This time she selects to go back to the main menu
        # and quits the application
        self.user_input.append('0')
        expected_output.append(msg.main_menu())
        expected_output.append(msg.option_input())
        self.user_input.append(app.MenuOptions.QUIT)
        expected_output.append(msg.quit())

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
        expected_output.append(msg.no_database_specified())
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
        expected_output.append(msg.new_database_created(self.database))
        expected_output.append(msg.main_menu())
        expected_output.append(msg.option_input())

        # Curious to see if there are any securities in the app already
        # he selects option 1 to view the securities.
        self.user_input.append(app.MenuOptions.VIEW_SECURITIES)
        expected_output.append(msg.view_securities([]))
        expected_output.append(msg.option_input())

        # As expected there are no securities so he returns to the main menu
        # and proceeds to option 2 to add securities
        self.user_input.append('0')
        expected_output.append(msg.main_menu())
        expected_output.append(msg.option_input())

        self.user_input.append(app.MenuOptions.ADD_SECURITIES)
        expected_output.append(msg.add_security_input())

        # He adds AMZN to the database
        self.user_input.append('AMZN')
        expected_output.append(msg.security_added('AMZN'))
        expected_output.append(msg.main_menu())
        expected_output.append(msg.option_input())

        # He now checks that the security has been added to the list
        self.user_input.append(app.MenuOptions.VIEW_SECURITIES)
        expected_output.append(msg.view_securities(['AMZN']))
        expected_output.append(msg.option_input())

        # Satisfied with the results he returns to the main menu
        # and closes the application
        self.user_input.append('0')
        expected_output.append(msg.main_menu())
        expected_output.append(msg.option_input())
        self.user_input.append(app.MenuOptions.QUIT)
        expected_output.append(msg.quit())

        # Method
        app.main()

        # Tests
        for actual, expected in zip(self.actual_output, expected_output):
            self.assertEqual(actual, expected)
        self.assertEqual(len(self.actual_output), len(expected_output))

if __name__ == '__main__':
    unittest.main()
