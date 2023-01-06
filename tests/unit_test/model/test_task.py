# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains unit tests for the Task class."""

# standard libraries
import unittest

# local sources
from pfdl_scheduler.model.service import Service
from pfdl_scheduler.model.task import Task
from pfdl_scheduler.model.counting_loop import CountingLoop

# 3rd party libraries
from antlr4.ParserRuleContext import ParserRuleContext


class TestTask(unittest.TestCase):
    """Tests for the methods of the Task class."""

    def test_init(self):
        task = Task()
        self.assertEqual(task.name, "")
        self.assertEqual(task.statements, [])
        self.assertEqual(task.variables, {})
        self.assertEqual(task.input_parameters, {})
        self.assertEqual(task.output_parameters, [])
        self.assertIsNone(task.context)
        self.assertEqual(task.context_dict, {})

        context = ParserRuleContext()
        task = Task(
            name="task1",
            statements=[Service(), CountingLoop(), CountingLoop(), Service()],
            variables={"var1": "val1", "var2": "val2"},
            input_parameters={"in1": "val4", "in2": "val5"},
            output_parameters=["out1", "out2"],
            context=context,
        )
        self.assertEqual(task.name, "task1")
        self.assertEqual(len(task.statements), 4)
        self.assertEqual(task.statements[0], Service())
        self.assertEqual(task.statements[1], CountingLoop())
        self.assertEqual(task.statements[2], CountingLoop())
        self.assertEqual(task.statements[3], Service())
        self.assertEqual(task.variables, {"var1": "val1", "var2": "val2"})
        self.assertEqual(task.input_parameters, {"in1": "val4", "in2": "val5"})
        self.assertEqual(task.output_parameters, ["out1", "out2"])
        self.assertEqual(task.context, context)
