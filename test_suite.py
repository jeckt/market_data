#!/usr/bin/env python

# NOTE(steve): a small script that runs all
# the tests in the project.
import unittest

if __name__ == '__main__':
    loader = unittest.TestLoader()

    test_suite = loader.loadTestsFromName('functional_tests')
    test_suite.addTests(loader.loadTestsFromName('cli_functional_tests'))
    test_suite.addTests(loader.discover('market_data/tests'))

    unittest.TextTestRunner(verbosity=1).run(test_suite)
