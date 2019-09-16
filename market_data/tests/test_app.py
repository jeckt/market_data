#!/usr/bin/env python

import os
import sys
import inspect
file_path = os.path.dirname(inspect.getfile(inspect.currentframe()))
sys.path.insert(0, os.path.split(os.path.split(file_path)[0])[0])

import unittest
from unittest.mock import patch
import market_data.app as app

class AppTests(unittest.TestCase):

    @patch('builtins.print', autospec=True)
    def test_app_terminates_if_no_database_provided(self, mock_print):
        app.main()
        mock_print.assert_called_with(app.NO_DATABASE_SPECIFIED_MESSAGE)

if __name__ == '__main__':
    unittest.main()
