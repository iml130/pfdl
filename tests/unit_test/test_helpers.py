# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains unit tests for the Helper functions."""

# standard libraries
import unittest

# local sources
import pfdl_scheduler.utils.helpers as helpers


class TestHelpers(unittest.TestCase):
    """
    Tests the methods of the Helper class
    """

    def setUp(self):
        pass

    def test_check_type(self):
        pass

    def test_is_string(self):
        self.assertTrue(helpers.is_string('"A string"'))
        self.assertTrue(helpers.is_string('"a string"'))
        self.assertTrue(helpers.is_string('"5"'))
        self.assertTrue(helpers.is_string('"?=!dasfj4235r"'))
        self.assertTrue(helpers.is_string('" "'))
        self.assertTrue(helpers.is_string('""'))
        self.assertTrue(helpers.is_string('"            "'))
        self.assertFalse(helpers.is_string("not a string"))
        self.assertFalse(helpers.is_string(5))
        self.assertFalse(helpers.is_string(True))

    def test_is_boolean(self):
        self.assertTrue(helpers.is_boolean("true"))
        self.assertTrue(helpers.is_boolean("false"))
        self.assertFalse(helpers.is_boolean("Not a boolean"))
        self.assertFalse(helpers.is_boolean("True"))
        self.assertFalse(helpers.is_boolean("False"))
        self.assertFalse(helpers.is_boolean('"a string"'))
        self.assertFalse(helpers.is_boolean('"5"'))
        self.assertFalse(helpers.is_boolean('"?=!dasfj4235r"'))

    def test_is_float(self):
        self.assertTrue(helpers.is_float("5.0"))
        self.assertTrue(helpers.is_float("123123.123124"))
        self.assertTrue(helpers.is_float("5"))
        self.assertFalse(helpers.is_float("not a number"))
        self.assertFalse(helpers.is_float("'5.0'"))
        self.assertFalse(helpers.is_float(""))

    def test_is_int(self):
        self.assertTrue(helpers.is_int("5"))
        self.assertFalse(helpers.is_int("5.0"))
        self.assertFalse(helpers.is_int("not a number"))
        self.assertFalse(helpers.is_int("'5'"))
        self.assertFalse(helpers.is_int(""))

    def test_is_number(self):
        self.assertTrue(helpers.is_number("5.0"))
        self.assertTrue(helpers.is_number("123123.123124"))
        self.assertTrue(helpers.is_number("5"))
        self.assertFalse(helpers.is_number("not a number"))
        self.assertFalse(helpers.is_number("'5.0'"))
        self.assertFalse(helpers.is_number(""))
