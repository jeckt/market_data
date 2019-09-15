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

    @patch('builtins.print')
    def test_add_securities_and_view_securities(self):
        # Alex has heard about this new command line app that can
        # store financial market data for him. He decides to open it
        # NOTE(steve): simulates ./market_data/app.py call on command line
        app.main()

        # Upon opening it, he is told that he has not specified
        # a database for the application to hook up to.
        help_msg = """
        Market Data is command line application provides collection, storage
        and retrieval of financial market data.

        To use the application either use the following commands:
            $ ./market_data/app.py $DATABASE_CONNECTION
        or
            $ python market_data/app.py $DATABASE_CONNECTION

        where $DATABASE_CONNECTION is the location of the json
        database connection file. If the file does not exist
        the application will create it.
        """
        mock_print.assert_called_with(help_msg)

        # Reading through the help provided, Alex decides to give it another
        # go and this time provides a database connection for the app to
        # create a new database file
        sys.argv[1] = 'testdb.json'
        app.main()

        # Upon providing the database connection string he is able to move
        # on to the next screen in the app.
        msg = """
        A new database has been created: testdb.json.

        Welcome!

        """
        msg += self.get_menu_options()
        mock_print.assert_called_with(msg)

        msg = "Option: "
        mock_print.assert_called_with(msg)

        # Curious to see if there are any securities in the app already
        # he select option 1 to view the securities.
        with patch('builtins.input', return_value='1'):
            msg = """
            Currently no securities have been added to database.

            """
            msg += self.get_menu_options()
            mock_print.assert_called_with(msg)

        # As expected there are no securities so he proceeds to option
        # 2 to add securities
        with patch('builtins.input', return_value='2'):
            msg = """
            Please type in the Yahoo ticker for the security you want to add:
            """
            mock_print.assert_called_with(msg)

        # He adds AMZN to the database
        with patch('builtins.input', return_value='AMZN'):
            msg = """
            AMZN has been added.

            Would you please to add another security? [y/n]:
            """
            mock_print.assert_called_with(msg)

        # Happy with just adding he selects 'n'
        with patch('builtins.input', return_value='n'):
            msg = self.get_menu_options()
            mock_print.assert_called_with(msg)

        # He now checks that the security has been added to the list
        with patch('builtins.input', return_value='1'):
            msg = """
            The following securities are in the database:

                1. AMZN

            """
            msg += self.get_menu_options()
            mock_print.assert_called_with(msg)

        # Satisfied with the results he closes the application
        with patch('builtins.input', return_value='3'):
            msg = """
            Thank you for using the Market Data Application. Bye!
            """
            mock_print.assert_called_with(msg)

if __name__ == '__main__':
    unittest.main()
