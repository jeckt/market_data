#!/usr/bin/env python

import os
import sys
import datetime
from decimal import Decimal
from enum import IntEnum, unique
from market_data.market_data import MarketData
from market_data.data import InvalidTickerError, InvalidDateError, NoDataError
import market_data.data_adapter as data_adapter

DATA_ADAPTER_SOURCE = data_adapter.DataAdapterSource.SQLITE3
TEST_MODE = False

app = MarketData()

def clear_screen():
    if not TEST_MODE:
        if os.name == 'nt':
            _ = os.system('cls')
        else:
            _ = os.system('clear')

@unique
class MenuOptions(IntEnum):
    VIEW_SECURITIES = 1
    ADD_SECURITIES = 2
    UPDATE_MARKET_DATA = 3
    QUIT = 4

def main():
    clear_screen()

    if len(sys.argv) > 1:
        conn_string = sys.argv[1]
        database = MarketData.Database(conn_string, DATA_ADAPTER_SOURCE)
        try:
            app.run(database=database)

            print(Messages.load_existing_database(database.conn_string))

        except data_adapter.DatabaseNotFoundError:
            da = data_adapter.get_adapter(database.source)
            da.create_database(database.conn_string)
            app.run(database=database)

            print(Messages.new_database_created(database.conn_string))

        running = True
        while running:
            print(Messages.main_menu())
            running = process_user_input()

    else:
        print(Messages.no_database_specified())

def process_user_input():
    running = True
    try:
        user_input = int(input(Messages.option_input()))

        if user_input == MenuOptions.QUIT:
            running = MainMenu.quit()

        elif user_input == MenuOptions.VIEW_SECURITIES:
            clear_screen()
            running = MainMenu.view_securities()

        elif user_input == MenuOptions.ADD_SECURITIES:
            running = MainMenu.add_securities()

        elif user_input == MenuOptions.UPDATE_MARKET_DATA:
            clear_screen()
            running = MainMenu.update_market_data()

        else:
            clear_screen()
            running = MainMenu.invalid_option()

    except ValueError:
        clear_screen()
        running = MainMenu.invalid_option()

    return running


class MainMenu:

    @staticmethod
    def quit():
        print(Messages.quit())

        return False

    @staticmethod
    def view_securities():
        return_to_main_menu = False
        while not return_to_main_menu:
            tickers = app.get_securities_list()
            print(Messages.view_securities(tickers))
            try:
                view_input = int(input(Messages.option_input()))
                clear_screen()

                if view_input == 0:
                    return_to_main_menu = True
                elif view_input > 0 and view_input <= len(tickers):
                    ticker = tickers[view_input - 1]
                    data = app.get_equity_data_series(ticker)
                    if len(data) > 0:
                        print(Messages.view_security_data(ticker, data))
                        input(Messages.any_key_to_return())
                        clear_screen()
                    else:
                        print(Messages.no_security_data(ticker))
                else:
                    print(Messages.invalid_option())

            except ValueError:
                clear_screen()
                print(Messages.invalid_option())

        clear_screen()
        return True

    @staticmethod
    def add_securities():
        ticker = input(Messages.add_security_input())

        app.add_security(ticker)

        clear_screen()
        print(Messages.security_added(ticker))

        return True

    @staticmethod
    def update_market_data():
        today = datetime.datetime.today()
        tickers = app.get_securities_list()
        for ticker in tickers:
            try:
                dt, _ = app.get_latest_equity_data(ticker)
                dt += datetime.timedelta(days=1)
            except InvalidTickerError:
                continue
            except NoDataError:
                dt = today

            date_list = []
            while dt <= today:
                if dt.weekday() < 5: # saturday = 5
                    date_list.append(dt)
                dt += datetime.timedelta(days=1)

            # TODO(steve): expose errors in debug mode!
            try:
                if len(date_list) > 0:
                    errors = app.bulk_update_market_data(ticker, date_list)
            except InvalidTickerError:
                pass
            except InvalidDateError:
                pass

        print(Messages.market_data_updated())

        return True

    @staticmethod
    def invalid_option():
        print(Messages.invalid_option())

        return True

class Messages:

    @staticmethod
    def main_menu():
        msg = 'Please select from the following options:\n\n'
        msg += f'\t{MenuOptions.VIEW_SECURITIES.value}. View Securities\n'
        msg += f'\t{MenuOptions.ADD_SECURITIES.value}. Add Securities\n'
        msg += f'\t{MenuOptions.UPDATE_MARKET_DATA.value}. Update Market Data\n'
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
    def no_security_data(ticker):
        return f'\nNo data avaiable for {ticker}'

    # TODO(steve): equity_data_series should be a collection type class
    # which stores dates and equity data for a single security
    @staticmethod
    def view_security_data(ticker, equity_data_series):
        TWO_PLACES = Decimal('1.00')
        msg = f'{ticker}\n'
        msg += f'{"=" * len(ticker)}\n\n'
        msg += 'Date         |   Open   |   High   |   Low    |   Close   \n'
        msg += '==========================================================\n'
        for data in equity_data_series:
            data_open = str(data[1].open.quantize(TWO_PLACES)).rjust(7)
            data_high = str(data[1].high.quantize(TWO_PLACES)).rjust(7)
            data_low = str(data[1].low.quantize(TWO_PLACES)).rjust(7)
            data_close = str(data[1].close.quantize(TWO_PLACES)).rjust(7)
            msg += f'{data[0].strftime("%d-%b-%Y")}  | '
            msg += f'{data_open}  | '
            msg += f'{data_high}  | '
            msg += f'{data_low}  | '
            msg += f'{data_close}  \n'
        return msg

    @staticmethod
    def any_key_to_return():
        return 'Press any key to return to view securities page...'

    @staticmethod
    def market_data_updated():
        return 'All market data has been updated...'

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
