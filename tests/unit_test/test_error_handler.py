# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains unit tests for the ErrorHandler class."""

# standard libraries
import unittest

# local sources
from pfdl_scheduler.validation.error_handler import ErrorHandler


class TestErrorHandler(unittest.TestCase):
    """Tests methods in the ErrorHandler class"""

    def setUp(self):
        self.error_handler = ErrorHandler("", False)
        self.error_handler_ext = ErrorHandler("", True)

    def test_print_error(self):
        self.error_handler.print_error("", syntax_error=True)
        self.assertEqual(self.error_handler.syntax_error_count, 1)
        self.assertEqual(self.error_handler.semantic_error_count, 0)
        self.assertEqual(self.error_handler.total_error_count, 1)

        self.error_handler.print_error("", syntax_error=False)
        self.assertEqual(self.error_handler.syntax_error_count, 1)
        self.assertEqual(self.error_handler.semantic_error_count, 1)
        self.assertEqual(self.error_handler.total_error_count, 2)

        self.error_handler_ext.print_error("", syntax_error=True)
        self.assertEqual(self.error_handler_ext.syntax_error_count, 1)
        self.assertEqual(self.error_handler_ext.semantic_error_count, 0)
        self.assertEqual(self.error_handler_ext.total_error_count, 1)

        self.error_handler_ext.print_error("", syntax_error=False)
        self.assertEqual(self.error_handler_ext.syntax_error_count, 1)
        self.assertEqual(self.error_handler_ext.semantic_error_count, 1)
        self.assertEqual(self.error_handler_ext.total_error_count, 2)

    def test_has_error(self):
        self.error_handler.total_error_count = 0
        self.error_handler_ext.total_error_count = 0
        self.assertFalse(self.error_handler.has_error())
        self.assertFalse(self.error_handler_ext.has_error())

        self.error_handler.total_error_count = 1
        self.error_handler_ext.total_error_count = 1
        self.assertTrue(self.error_handler.has_error())
        self.assertTrue(self.error_handler_ext.has_error())
