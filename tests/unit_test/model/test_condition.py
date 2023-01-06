# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains unit tests for the Condition class."""

# standard libraries
import unittest

# local sources
from pfdl_scheduler.model.condition import Condition
from pfdl_scheduler.model.service import Service
from pfdl_scheduler.model.task_call import TaskCall

# 3rd party libraries
from antlr4.ParserRuleContext import ParserRuleContext


class TestCondition(unittest.TestCase):
    """Tests for the methods of the Condition class."""

    def test_init(self):
        condition = Condition()
        self.assertIsNone(condition.expression)
        self.assertEqual(condition.passed_stmts, [])
        self.assertEqual(condition.failed_stmts, [])
        self.assertIsNone(condition.context)
        self.assertEqual(condition.context_dict, {})

        context = ParserRuleContext()
        condition = Condition({"a": 1}, [Service("service")], [TaskCall("task")], context=context)
        self.assertEqual(condition.expression, {"a": 1})
        self.assertEqual(condition.passed_stmts, [Service("service")])
        self.assertEqual(condition.failed_stmts, [TaskCall("task")])
        self.assertEqual(condition.context, context)
        self.assertEqual(condition.context_dict, {})
