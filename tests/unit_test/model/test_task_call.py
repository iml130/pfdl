# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains unit tests for the TaskCall class."""

# standard libraries
import unittest

# local sources
from pfdl_scheduler.model.task_call import TaskCall


class TestTaskCall(unittest.TestCase):
    """Tests for the methods of the TaskCall class."""

    def test_init(self):
        task_call = TaskCall()
        self.assertEqual(task_call.name, "")
        self.assertEqual(task_call.input_parameters, [])
        self.assertEqual(task_call.output_parameters, {})

        task_call = TaskCall(
            "task_name",
            ["input1", "input2"],
            {"output1": "output1_value", "output2": "output2_value"},
        )
        self.assertEqual(task_call.name, "task_name")
        self.assertEqual(task_call.input_parameters, ["input1", "input2"])
        self.assertEqual(
            task_call.output_parameters, {"output1": "output1_value", "output2": "output2_value"}
        )
