#!/usr/bin/env python

import sys
from market_data.market_data import MarketData
from market_data.data_adapter import DataAdapter, DatabaseNotFoundError

MENU_OPTIONS = """
Please select from the following options:
    1. View Securities
    2. Add a Security
    3. Quit
"""

INVALID_MENU_OPTION_MSG = 'The option selected is invalid'

NO_DATABASE_SPECIFIED_MSG = """
Market Data is command line application that provides
collection, storage and retrieval of financial market data.

To use the application either use the following commands:
    $ ./market_data/app.py $DATABASE_CONNECTION
or
    $ python market_data/app.py $DATABASE_CONNECTION

where $DATABASE_CONNECTION is the location of the json
database connection file. If the file does not exist
the application will create it.
"""

NEW_DATABASE_CREATED_MSG = 'Welcome! A new database has been created: {0}'

DATABASE_LOADED_MSG = 'Welcome! Database {0} has been loaded'

QUIT_MSG = 'Thank you for using the Market Data Application. Goodbye!'

VIEW_NO_SECURITIES = 'Currently no securities have been added to database.'

USER_OPTION_INPUT = 'Option: '
QUIT_OPTION = '3'
VIEW_SECURITIES_OPTION = '1'

def get_new_database_created_msg(db):
    return NEW_DATABASE_CREATED_MSG.format(db)

def get_load_existing_database_msg(db):
    return DATABASE_LOADED_MSG.format(db)

def process_user_input():
    user_input = input(USER_OPTION_INPUT)
    if user_input == QUIT_OPTION:
        print(QUIT_MSG)
        return False
    elif user_input == VIEW_SECURITIES_OPTION:
        print(VIEW_NO_SECURITIES)
        print(MENU_OPTIONS)
    else:
        print(INVALID_MENU_OPTION_MSG)
        print(MENU_OPTIONS)

    return True

def main():
    if len(sys.argv) > 1:
        conn_string = sys.argv[1]
        app = MarketData()
        try:
            app.run(conn_string)

            print(get_load_existing_database_msg(conn_string))
            print(MENU_OPTIONS)
        except DatabaseNotFoundError:
            DataAdapter.create_database(conn_string)
            app.run(conn_string)

            print(get_new_database_created_msg(conn_string))
            print(MENU_OPTIONS)

        # TODO(steve): probably better to use a running global parameter
        # to make it more readable
        while process_user_input(): pass
    else:
        print(NO_DATABASE_SPECIFIED_MSG)

if __name__ == '__main__':
    main()
