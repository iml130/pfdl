# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains unit tests for the CountingLoop class."""

# standard libraries
import unittest

# local sources
from pfdl_scheduler.model.counting_loop import CountingLoop
from pfdl_scheduler.model.service import Service
from pfdl_scheduler.model.task_call import TaskCall

# 3rd party libraries
from antlr4.ParserRuleContext import ParserRuleContext


class TestCountingLoop(unittest.TestCase):
    """Tests for the methods of the CountingLoop class."""

    def test_init(self):
        counting_loop = CountingLoop()
        self.assertEqual(counting_loop.statements, [])
        self.assertEqual(counting_loop.counting_variable, "")
        self.assertEqual(counting_loop.limit, "")
        self.assertEqual(counting_loop.parallel, False)
        self.assertIsNone(counting_loop.context)

        context = ParserRuleContext()
        statements = [Service(name="service1"), TaskCall(name="task1")]
        counting_loop = CountingLoop(
            statements=statements,
            counting_variable="i",
            limit="10",
            parallel=True,
            context=context,
        )
        self.assertEqual(counting_loop.statements, statements)
        self.assertEqual(counting_loop.counting_variable, "i")
        self.assertEqual(counting_loop.limit, "10")
        self.assertEqual(counting_loop.parallel, True)
        self.assertEqual(counting_loop.context, context)
