#!/usr/bin/env python

# NOTE(steve): a small script that runs all
# the tests in the project.
import os
import unittest

if __name__ == '__main__':
    loader = unittest.TestLoader()

    test_suite = unittest.TestSuite()
    test_suite.addTests(loader.discover('market_data/tests'))
    for f in os.listdir('tests'):
        filename, ext = os.path.splitext(f)
        if ext == '.py':
            module = f'tests.{filename}'
            test_suite.addTests(loader.loadTestsFromName(module))

    unittest.TextTestRunner(verbosity=1).run(test_suite)
