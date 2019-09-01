#!/usr/bin/env python

import unittest
from unittest import skip
import datetime
from decimal import Decimal
from market_data.market_data import MarketData

class FunctionalTests(unittest.TestCase):

    def test_add_security_into_app(self):
        # Carol opens up the application
        app = MarketData()
        app.run()

        # Carol adds Amazon(AMZN) to the app as
        # she would like to start tracking the
        # daily market price.
        ticker = 'AMZN'
        app.add_security(ticker)

        # She then checks to make sure that
        # the actual stock has been added to
        # the list of securities
        self.assertTrue(ticker in app.get_securities_list())

        # Satisfied that it is indeed in the app
        # she closes it and gets on with her day
        app.close()


    # NOTE(steve): user is a machine that runs on a 
    # scheduler and collects the required data this
    # will be coded into a script
    # TODO(steve): a terrible functional test as
    # it does not actually test that the data
    # is correct after executing functions!!!
    @skip
    def test_update_market_data_in_app(self):
        # Jarvis (machine) opens up the application
        app = MarketData()
        app.run()

        # Jarvis gets the list of securities that
        # he needs to update
        securities = app.get_securities_list()

        # He checks that the securities in the
        # list are what he expects
        expected_sec_list = ['AMZN', 'TLS.AX']
        self.assertEqual(securities, expected_sec_list)

        # Jarvis proceeds to update each security
        # in the list with the most recent available
        # market data
        # TODO(steve): mock this so that it always 
        # returns a valid date for this test case
        dt = datetime.datetime.today()
        for sec in securities:
            app.update_security_data(sec, dt)

        # Jarvis closes the application once his
        # job is complete
        app.close()

if __name__ == '__main__':
    unittest.main()
