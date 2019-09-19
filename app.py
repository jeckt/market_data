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

INVALID_MENU_OPTION_MSG = """
    The option selected is invalid.
"""
INVALID_MENU_OPTION_MSG += MENU_OPTIONS

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

NEW_DATABASE_CREATED_MSG = """
    Welcome! A new database has been created: {0}.
"""
NEW_DATABASE_CREATED_MSG += MENU_OPTIONS

DATABASE_LOADED_MSG = """
    Welcome! Database {0} has been loaded.
"""
DATABASE_LOADED_MSG += MENU_OPTIONS

def get_new_database_created_msg(db):
    return NEW_DATABASE_CREATED_MSG.format(db)

def get_load_existing_database_msg(db):
    return DATABASE_LOADED_MSG.format(db)

def process_user_input():
    user_input = input("Option: ")
    print(INVALID_MENU_OPTION_MSG)
    return True

def main():
    if len(sys.argv) > 1:
        conn_string = sys.argv[1]
        app = MarketData()
        try:
            app.run(conn_string)
            print(get_load_existing_database_msg(conn_string))
        except DatabaseNotFoundError:
            DataAdapter.create_database(conn_string)
            app.run(conn_string)
            print(get_new_database_created_msg(conn_string))

        return True
    else:
        print(NO_DATABASE_SPECIFIED_MSG)
        return False

# TODO(steve): Is this really the most efficient/clean way to do this?!?
if __name__ == '__main__':
    if not main(): sys.exit(0)
    while process_user_input(): pass
