#
# Vince Charming (c) 2019
#
"""
Tests for general utilities
"""

import os
import sys
import unittest

from uuid import UUID

# Sets up an absolute path to the python directory
DIR_PATH = os.path.dirname(os.path.join(os.getcwd(), __file__))
sys.path.append(os.path.normpath(os.path.join(DIR_PATH, '..')))
import utils.general_utils as gen_utils

__author__ = 'vcharming'


class TestGeneralUtils(unittest.TestCase):

    def test_is_valid_uuid(self):
        test_uuids_and_results = [
            ('00000000000000000000000000000000', True),
            ('00000000-0000-0000-0000-000000000000', True),
            ('725ae085a794e6d0bfcc9be191a9d5a0', True),
            ('725ae085-a794-e6d0-bfcc-9be191a9d5a0', True),
            ('00000000-000000000000000000000-000', True),
            (UUID('412ae085-a794-e6d0-bfcc-9be191a9d5a0'), True),
            ('0000000000000000000000000000000', False),
            (0o1234567, False),
            ('725ae085a794e6d0bfcc', False)]
        for test_uuid, result in test_uuids_and_results:
            if result:
                self.assertTrue(gen_utils.is_valid_uuid(test_uuid))
            else:
                self.assertFalse(gen_utils.is_valid_uuid(test_uuid))


def suite():
    functions_suite = unittest.TestLoader().loadTestsFromTestCase(TestGeneralUtils)
    return unittest.TestSuite([functions_suite])


if __name__ == "__main__":
    text_test_result = unittest.TextTestRunner(verbosity=1).run(suite())
    sys.exit(0 if text_test_result.wasSuccessful() else 1)
