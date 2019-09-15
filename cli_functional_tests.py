#!/usr/bin/env python

import unittest
from unittest.mock import patch
import sys
import market_data.app as app

class CommandLineInterfaceTests(unittest.TestCase):

    def get_menu_options(self):
        return """
        Please select from the following options:
                1. View Securities
                2. Add a Security
                3. Quit
        """

    @patch('builtins.input', autospec=True)
    def test_add_securities_and_view_securities(self, mock_input):
        # Alex has heard about this new command line app that can
        # store financial market data for him. He decides to open it
        # NOTE(steve): simulates ./market_data/app.py call on command line
        with patch('builtins.print', autospec=True) as mock_print:
            app.main()

            # Upon opening it, he is told that he has not specified
            # a database for the application to hook up to.
            msg = """
            Market Data is command line application provides collection,
            storage and retrieval of financial market data.

            To use the application either use the following commands:
                $ ./market_data/app.py $DATABASE_CONNECTION
            or
                $ python market_data/app.py $DATABASE_CONNECTION

            where $DATABASE_CONNECTION is the location of the json
            database connection file. If the file does not exist
            the application will create it.
            """
            mock_print.assert_called_with(msg)

        # Reading through the help provided, Alex decides to give it another
        # go and this time provides a database connection for the app to
        # create a new database file
        # NOTE(steve): we patch the process user input function here
        # so that we can control the loop later in the test otherwise
        # we would not be able to test the changes in user input requests
        sys.argv = ['./market_data/app.py', 'testdb.json']
        with patch('builtins.print', autospec=True) as mock_print:
            with patch('market_data.app.process_user_input', autospec=True):
                app.main()

            # Upon providing the database connection string he is able 
            # to move on to the next screen in the app.
            msg = """
            A new database has been created: testdb.json.

            Welcome!

            """
            msg += self.get_menu_options()
            mock_print.assert_called_with(msg)

        with patch('builtins.print', autospec=True) as mock_print:
            # Curious to see if there are any securities in the app already
            # he select option 1 to view the securities.
            mock_input.return_value = '1'
            app.process_user_input()
            mock_input.assert_called_with('Option: ')

            msg = """
            Currently no securities have been added to database.

            """
            msg += self.get_menu_options()
            mock_print.assert_called_with(msg)

        with patch('builtins.print', autospec=True) as mock_print:
            # As expected there are no securities so he proceeds to option
            # 2 to add securities
            mock_input.return_value = '2'
            app.process_user_input()
            mock_input.assert_called_with('Option: ')

        with patch('builtins.print', autospec=True) as mock_print:
            # He adds AMZN to the database
            mock_input.return_value = 'AMZN'
            app.process_user_input()
            msg = """
            Please type in the Yahoo ticker for the security you want to add:
            """
            mock_input.assert_called_with(msg)

            msg = """
            AMZN has been added.

            """
            mock_print.assert_called_with(msg)

        with patch('builtins.print', autospec=True) as mock_print:
            # He is then asked if he would like to add another security. 
            # Happy with just adding he selects 'n'
            mock_input.return_value = 'n'
            app.process_user_input()
            msg = """
            Would you please to add another security? [y/n]:
            """
            mock_input.assert_called_with(msg)

            msg = self.get_menu_options()
            mock_print.assert_called_with(msg)

        with patch('builtins.print', autospec=True) as mock_print:
            # He now checks that the security has been added to the list
            mock_input.return_value = '1'
            app.process_user_input()
            msg = """
            The following securities are in the database:

                1. AMZN

            """
            mock_input.assert_called_with('Option: ')

            msg += self.get_menu_options()
            mock_print.assert_called_with(msg)

        with patch('builtins.print', autospec=True) as mock_print:
            # Satisfied with the results he closes the application
            mock_input.return_value = '3'
            app.process_user_input()
            mock_input.assert_called_with('Option: ')

            msg = """
            Thank you for using the Market Data Application. Bye!
            """
            mock_print.assert_called_with(msg)

if __name__ == '__main__':
    unittest.main()
