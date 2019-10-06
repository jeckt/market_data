#!/usr/bin/env python

import os
import sys
import inspect
file_path = os.path.dirname(inspect.getfile(inspect.currentframe()))
sys.path.insert(0, os.path.split(os.path.split(file_path)[0])[0])

import unittest
import json
from market_data.json_data_adapter import TextDataModel
import market_data.tests.utils as test_utils

class TextDataModelTests(unittest.TestCase):

    def setUp(self):
        ticker, dt, equity_data = test_utils.get_expected_equity_data()
        self.ticker, self.dt, self.equity_data = ticker, dt, equity_data
        self.date_string = dt.strftime('%d-%b-%Y')

    def get_json_from_dict_data(self):
        data_dict = {
            "securities": [self.ticker, 'GOOG', 'TLS.AX'],
            self.ticker: {
                self.date_string: {
                    'open': '1898.00',
                    'high': '1903.79',
                    'low': '1856.00',
                    'close': '1889.98',
                    'adj_close': '1889.98',
                    'volume': int(5718000)
                }
            }
        }
        json_data = json.dumps(data_dict)

        return json_data

    def get_text_data_model_data(self):
        data = TextDataModel()
        data.securities = [self.ticker, 'GOOG', 'TLS.AX']
        data.equity_data = {
            self.ticker: { self.date_string: self.equity_data }
        }

        return data

    def test_equality(self):
        data_1 = self.get_text_data_model_data()
        data_2 = self.get_text_data_model_data()
        self.assertEqual(data_1, data_2)

    def test_json_encoder_can_serialise_text_data_model(self):
        # set up
        data = self.get_text_data_model_data()

        # method
        actual_data = json.dumps(data, default=TextDataModel.json_encoder)

        # expected output
        json_data = self.get_json_from_dict_data()

        # test
        self.assertEqual(json_data, actual_data)

    def test_json_decoder_can_deserialise_text_data_model(self):
        # set up
        json_data = self.get_json_from_dict_data()

        # method
        actual_data = json.loads(json_data,
                                 object_hook=TextDataModel.json_decoder)

        # expected output
        expected_data = self.get_text_data_model_data()

        # test
        self.assertEqual(expected_data, actual_data)

if __name__ == '__main__':
    unittest.main()
