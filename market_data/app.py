#!/usr/bin/env python

NO_DATABASE_SPECIFIED_MESSAGE = """
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
def main():
    print(NO_DATABASE_SPECIFIED_MESSAGE)

if __name__ == '__main__':
    main()
