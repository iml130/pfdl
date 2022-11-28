# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains unit tests tests for the Scheduler class."""

# standard libraries
import unittest
from pfdl_scheduler.model.struct import Struct

# local sources
from pfdl_scheduler.scheduler import Scheduler
from pfdl_scheduler.api.task_api import TaskAPI


class TestScheduler(unittest.TestCase):
    def setUp(self) -> None:
        self.scheduler = Scheduler("tests/test_files/scheduling/simple_task.pfdl")

    def test_check_expression(self):
        expression = "True"
        dummy_context = TaskAPI(None, None)
        self.assertTrue(self.scheduler.check_expression(expression, dummy_context))

        expression = {"left": {"left": 10, "binOp": "+", "right": 5}, "binOp": "==", "right": 15}
        self.assertTrue(self.scheduler.check_expression(expression, dummy_context))

        expression = {"left": {"left": 10, "binOp": "+", "right": 5}, "binOp": "==", "right": 20}
        self.assertFalse(self.scheduler.check_expression(expression, dummy_context))

    def test_execute_expression(self):
        dummy_context = TaskAPI(None, None)

        self.assertEqual(self.scheduler.execute_expression(True, dummy_context), True)
        self.assertEqual(self.scheduler.execute_expression(False, dummy_context), False)
        self.assertEqual(self.scheduler.execute_expression("true", dummy_context), "true")
        self.assertEqual(self.scheduler.execute_expression("false", dummy_context), "false")
        self.assertEqual(self.scheduler.execute_expression("True", dummy_context), "True")
        self.assertEqual(self.scheduler.execute_expression("False", dummy_context), "False")
        self.assertEqual(self.scheduler.execute_expression("a_string", dummy_context), "a_string")
        self.assertEqual(self.scheduler.execute_expression("5", dummy_context), "5")
        self.assertEqual(self.scheduler.execute_expression(5, dummy_context), 5)

        expression = {"left": 10, "binOp": "+", "right": 5}
        self.assertEqual(self.scheduler.execute_expression(expression, dummy_context), 15)

        expression = {"left": 10, "binOp": "-", "right": 5}
        self.assertEqual(self.scheduler.execute_expression(expression, dummy_context), 5)

        expression = {"left": 10, "binOp": "*", "right": 5}
        self.assertEqual(self.scheduler.execute_expression(expression, dummy_context), 50)

        expression = {"left": 10, "binOp": "/", "right": 5}
        self.assertEqual(self.scheduler.execute_expression(expression, dummy_context), 2)

        expression = {"left": {"left": 10, "binOp": "+", "right": 5}, "binOp": "==", "right": 15}
        self.assertEqual(self.scheduler.execute_expression(expression, dummy_context), True)

        expression = {"left": {"left": 10, "binOp": "+", "right": 5}, "binOp": "==", "right": 20}
        self.assertEqual(self.scheduler.execute_expression(expression, dummy_context), False)

        expression = {"left": {"left": 10, "binOp": "*", "right": 5}, "binOp": "-", "right": 20}
        self.assertEqual(self.scheduler.execute_expression(expression, dummy_context), 30)

        expression = {"left": ["variable", "parts_count"], "binOp": "==", "right": 10}
        access_func = lambda var, context: Struct(attributes={"parts_count": 10})
        self.scheduler.register_variable_access_function(access_func)

        self.assertEqual(self.scheduler.execute_expression(expression, dummy_context), True)
