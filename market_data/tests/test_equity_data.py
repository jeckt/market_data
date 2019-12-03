#!/usr/bin/env python

import os
import sys
import inspect
file_path = os.path.dirname(inspect.getfile(inspect.currentframe()))
sys.path.insert(0, os.path.split(os.path.split(file_path)[0])[0])

import unittest
from decimal import Decimal

from market_data.data import EquityData

# TODO(steve): test to make sure the decimal representations
# that are created are correct. e.g. Decimal(1793.03) != 1793.03
# to do that you need to pass in a string i.e. Decimal('1793.03')
class EquityDataTests(unittest.TestCase):

    def test_defaults_fields_to_zero(self):
        d = EquityData()
        self.assertEqual(d.open, 0)
        self.assertEqual(d.high, 0)
        self.assertEqual(d.low, 0)
        self.assertEqual(d.close, 0)
        self.assertEqual(d.adj_close, 0)
        self.assertEqual(d.volume, 0)

    def test_all_fields_price_fields_are_decimals(self):
        d = EquityData()
        self.assertIsInstance(d.open, Decimal)
        self.assertIsInstance(d.high, Decimal)
        self.assertIsInstance(d.low, Decimal)
        self.assertIsInstance(d.close, Decimal)
        self.assertIsInstance(d.adj_close, Decimal)

    def test_volume_field_is_an_integer(self):
        d = EquityData(volume=400.5)
        self.assertIsInstance(d.volume, int)

    def test_two_equity_data_objects_equal(self):
        d1 = EquityData(open=10, high=15.5, low=9.1, close=12.33,
                       adj_close=12.33, volume=32000)
        d2 = EquityData(open=10, high=15.5, low=9.1, close=12.33,
                       adj_close=12.33, volume=32000)
        self.assertEqual(d1, d2)

    def test_two_equity_data_objects_not_equal(self):
        d1 = EquityData(open=10, high=15.5, low=9.1, close=12.33,
                       adj_close=12.33, volume=32000)
        d2 = EquityData(open=1, high=5.5, low=0.1, close=1.28,
                       adj_close=1.28, volume=2240)
        self.assertNotEqual(d1, d2)

if __name__ == '__main__':
    unittest.main()
