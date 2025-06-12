import argparse
import os
import sys
import unittest

RELATIVE_TEST_DIR = "../tests/"

def register_subparser(subparser):
    # No additional CLI options needed for now
    return


def main(args):
    # Determine the absolute path to the tests directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    test_dir = os.path.normpath(os.path.join(script_dir, RELATIVE_TEST_DIR))

    print(f"Loading tests from dir {test_dir}")

    # Discover and load all tests in the directory
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=test_dir, pattern="test_*.py")

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with non-zero status if any tests failed
    if not result.wasSuccessful():
        sys.exit(1)
