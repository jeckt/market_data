#!/usr/bin/env python

import sys
from enum import IntEnum, unique
from market_data.market_data import MarketData
from market_data.data_adapter import DataAdapter, DatabaseNotFoundError

app = MarketData()

@unique
class MenuOptions(IntEnum):
    VIEW_SECURITIES = 1
    ADD_SECURITIES = 2
    QUIT = 3

def main():
    if len(sys.argv) > 1:
        conn_string = sys.argv[1]
        try:
            app.run(conn_string)

            print(Messages.load_existing_database(conn_string))
            print(Messages.main_menu())

        except DatabaseNotFoundError:
            DataAdapter.create_database(conn_string)
            app.run(conn_string)

            print(Messages.new_database_created(conn_string))
            print(Messages.main_menu())

        # TODO(steve): probably better to use a running global parameter
        # to make it more readable
        while process_user_input(): pass

    else:
        print(Messages.no_database_specified())

def process_user_input():
    try:
        user_input = int(input(Messages.option_input()))

        if user_input == MenuOptions.QUIT:
            print(Messages.quit())
            return False

        elif user_input == MenuOptions.VIEW_SECURITIES:
            return_to_main_menu = False
            while not return_to_main_menu:
                tickers = app.get_securities_list()
                print(Messages.view_securities(tickers))
                try:
                    view_input = int(input(Messages.option_input()))

                    if view_input == 0:
                        return_to_main_menu = True
                    else:
                        print(Messages.invalid_option())

                except ValueError:
                    print(Messages.invalid_option())

        elif user_input == MenuOptions.ADD_SECURITIES:
            ticker = input(Messages.add_security_input())

            app.add_security(ticker)

            print(Messages.security_added(ticker))

        else:
            print(Messages.invalid_option())

    except ValueError:
        print(Messages.invalid_option())

    print(Messages.main_menu())
    return True

class Messages:

    @staticmethod
    def main_menu():
        msg = 'Please select from the following options:\n\n'
        msg += f'\t{MenuOptions.VIEW_SECURITIES.value}. View Securities\n'
        msg += f'\t{MenuOptions.ADD_SECURITIES.value}. Add Securities\n'
        msg += f'\t{MenuOptions.QUIT.value}. Quit\n\n'
        return msg

    @staticmethod
    def invalid_option():
        return 'The option selected is invalid'

    @staticmethod
    def option_input():
        return 'Option: '

    @staticmethod
    def view_securities(tickers):
        if len(tickers) > 0:
            msg = '\nThe following securities are in the database:\n\n'
            msg += '0. Return to Main Menu\n'
            for num, ticker in enumerate(tickers):
                msg += f'{num + 1}. {ticker}\n'
        else:
            msg = '\nCurrently no securities have been added to database.\n\n'
            msg += '0. Return to Main Menu\n'

        return msg

    @staticmethod
    def add_security_input():
        return 'Enter Yahoo ticker for the security you want to add: '

    @staticmethod
    def security_added(ticker):
        msg = f'\n{ticker} has been added'
        return msg

    @staticmethod
    def quit():
        return '\nThank you for using the Market Data Application. Goodbye!'

    @staticmethod
    def no_database_specified():
        return """
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

    @staticmethod
    def new_database_created(db):
        msg = f'Welcome! A new database has been created: {db}\n\n'
        return msg

    @staticmethod
    def load_existing_database(db):
        msg = f'Welcome! Database {db} has been loaded\n\n'
        return msg

if __name__ == '__main__':
    main()
