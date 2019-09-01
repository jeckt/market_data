#!/usr/bin/env python

import os
import inspect
os.chdir((os.path.dirname(inspect.getfile(inspect.currentframe()))))

import unittest
from unittest import skip
from unittest.mock import patch

from market_data import MarketData
from market_data import NotInitialisedError

class MarketDataTests(unittest.TestCase):

    def test_app_not_initialised_before_use_throws_error(self):
        app = MarketData()

        with self.assertRaises(NotInitialisedError):
            sec_list = app.get_securities_list()

    # NOTE(steve): Testing two functions instead of each 
    # individually as individual tests will require
    # knowledge of the implementation.
    def test_add_and_get_securities_list(self):
        expected_sec_list = ['AMZN', 'GOOG', 'TLS.AX']

        app = MarketData()
        app.run()

        for sec in expected_sec_list:
            app.add_security(sec)

        actual_sec_list = app.get_securities_list()
        self.assertEqual(actual_sec_list, expected_sec_list)

if __name__ == '__main__':
    unittest.main()
