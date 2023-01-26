# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains unit tests for the Array class."""

# standard libraries
import copy
import unittest

# local sources
from pfdl_scheduler.model.array import Array

# 3rd party libraries
from antlr4.ParserRuleContext import ParserRuleContext


class TestArray(unittest.TestCase):
    """Tests for the methods of the Array class."""

    def test_init(self):
        array = Array()
        self.assertEqual(array.type_of_elements, "")
        self.assertEqual(array.values, [])
        self.assertEqual(array.length, -1)
        self.assertIsNone(array.context)

        context = ParserRuleContext()
        array = Array("int", [1, 2, 3], context)
        self.assertEqual(array.type_of_elements, "int")
        self.assertEqual(array.values, [1, 2, 3])
        self.assertEqual(array.length, 3)
        self.assertEqual(array.context, context)

    def test_repr(self):
        # test with defined length
        array = Array("int", [1, 2, 3])
        self.assertEqual(repr(array), "int[3]")

        # test with undefined length
        array = Array("int", [])
        self.assertEqual(repr(array), "int[]")

    def test_str(self):
        # test with defined length
        array = Array("int", [1, 2, 3])
        self.assertEqual(str(array), "int[3]")

        # test with undefined length
        array = Array("int", [])
        self.assertEqual(str(array), "int[]")

    def test_add(self):
        array = Array("int", [1, 2, 3])
        self.assertEqual(array + "test", "int[3]test")
        self.assertEqual("test" + array, "testint[3]")

    def test_deepcopy(self):
        # do not test context, as we cant control the copying of it
        array = Array("int", [1, 2, 3])
        copied_array = copy.deepcopy(array)
        self.assertEqual(copied_array.type_of_elements, "int")
        self.assertEqual(copied_array.values, [1, 2, 3])
        self.assertEqual(copied_array.length, 3)

    def test_append_value(self):
        array = Array("int", [])
        array.append_value(1)
        self.assertEqual(array.values, [1])
        self.assertEqual(array.length, 1)

        array.append_value(2)
        self.assertEqual(array.values, [1, 2])
        self.assertEqual(array.length, 2)

    def test_length_defined(self):
        # test with defined length
        array = Array("int", [1, 2, 3])
        self.assertTrue(array.length_defined())

        # test with undefined length
        array = Array("int", [])
        self.assertFalse(array.length_defined())
