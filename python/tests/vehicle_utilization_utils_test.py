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
import utils.vehicle_utilization_utils as v_u_utils

__author__ = 'vcharming'


class TestVehicleUtilizationUtils(unittest.TestCase):

    def test_is_valid_row(self):
        test_rows_and_results = [
            (['VEHICLE0008', 'autonomous', '2019-03-11 19:57:37', '2019-03-11 19:58:12', 'vince.charming', 'Team V'], True),
            (['vehicleabcd', 'u', '2019-03-11 19:57:37', '2019-03-11 19:58:12', 'vince', 'team V'], True),
            (['VEHICLE008', 'autonomous', '2019-03-11 19:57:37', '2019-03-11 19:58:12', 'vince.charming', 'Team V'], False),
            (['CARRRR0008', 'autonomous', '2019-03-11 19:57:37', '2019-03-11 19:58:12', 'vince.charming', 'Team V'], False),
            (['VEHICLE0008', 'driving', '2019-03-11 19:57:37', '2019-03-11 19:58:12', 'vince.charming', 'Team V'], False),
            (['VEHICLE0008', 'autonomous', '', '2019-03-11 19:58:12', 'vince.charming', 'Team V'], False),
            (['VEHICLE0008', 'autonomous', '2019-03--11 19:57:37', '2019-03-11 19:58:12', 'vince.charming', 'Team V'], False),
            (['VEHICLE0008', 'autonomous', '2019-03-11 19:57:37', '', 'vince.charming', 'Team V'], False),
            (['VEHICLE0008', 'autonomous', '2019-03-11 19:57:37', '2019-03--11 19:58:12', 'vince.charming', 'Team V'], False),
            (['VEHICLE0008', 'autonomous', '2019-03-11 19:58:12', '2019-03-11 19:57:37', 'vince.charming', 'Team V'], False),
            (['VEHICLE0008', 'autonomous', '2019-03-11 19:57:37', '2019-03-11 19:58:12', '', 'Team V'], False),
            (['VEHICLE0008', 'autonomous', '2019-03-11 19:57:37', '2019-03-11 19:58:12', 'vince.charming', 'V'], False)]
        for test_row, result in test_rows_and_results:
            if result:
                self.assertTrue(v_u_utils.is_valid_row(test_row))
            else:
                self.assertFalse(v_u_utils.is_valid_row(test_row))


def suite():
    functions_suite = unittest.TestLoader().loadTestsFromTestCase(TestVehicleUtilizationUtils)
    return unittest.TestSuite([functions_suite])


if __name__ == "__main__":
    text_test_result = unittest.TextTestRunner(verbosity=1).run(suite())
    sys.exit(0 if text_test_result.wasSuccessful() else 1)
