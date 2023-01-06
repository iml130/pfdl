# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains unit tests for the WhileLoop class."""

# standard libraries
import unittest

# local sources
from pfdl_scheduler.model.service import Service
from pfdl_scheduler.model.task_call import TaskCall
from pfdl_scheduler.model.while_loop import WhileLoop

# 3rd party libraries
from antlr4.ParserRuleContext import ParserRuleContext


class TestWhileLoop(unittest.TestCase):
    """Tests for the methods of the WhileLoop class."""

    def test_init(self):
        while_loop = WhileLoop()
        self.assertEqual(while_loop.statements, [])
        self.assertEqual(while_loop.expression, {})
        self.assertIsNone(while_loop.context)
        self.assertEqual(while_loop.context_dict, {})

        statements = [Service(), TaskCall()]
        expression = "True"
        context = ParserRuleContext()
        while_loop = WhileLoop(statements, expression, context)
        self.assertIsInstance(while_loop, WhileLoop)
        self.assertEqual(while_loop.statements, statements)
        self.assertEqual(while_loop.expression, expression)
        self.assertEqual(while_loop.context, context)
        self.assertEqual(while_loop.context_dict, {})
