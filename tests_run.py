import unittest
import os

def discover_and_run_tests():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Specify the start directory and pattern
    start_dir = './'
    pattern = 'test_*.py'

    # Discover tests
    print(f"Discovering tests in {start_dir} with pattern {pattern}")
    discovered_suite = loader.discover(start_dir, pattern=pattern)

    # Print discovered tests
    for test_group in discovered_suite:
        for test in test_group:
            # print(f"Discovered test: {test}")
            pass

    # Add discovered tests to the suite
    suite.addTests(discovered_suite)

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

if __name__ == '__main__':
    discover_and_run_tests()