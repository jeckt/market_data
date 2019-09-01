#!/usr/bin/env python

import unittest
import datetime
from decimal import Decimal
from market_data.market_data import MarketData

class FunctionalTests(unittest.TestCase):

    # NOTE(steve): user is a machine that runs on a 
    # scheduler and collects the required data this
    # will be coded into a script
    def test_update_market_data_in_app(self):
        # Jarvis (machine) opens up the application
        app = MarketData()
        app.run()

        # Jarvis gets the list of securities that
        # he needs to update
        securities = app.get_securities_list()

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
