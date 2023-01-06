# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains unit tests for the Parallel class."""

# standard libraries
import unittest

# local sources
from pfdl_scheduler.model.parallel import Parallel
from pfdl_scheduler.model.task_call import TaskCall

# 3rd party libraries
from antlr4.ParserRuleContext import ParserRuleContext


class TestParallel(unittest.TestCase):
    """Tests for the methods of the Parallel class."""

    def test_init(self):
        parallel = Parallel()
        self.assertEqual(parallel.task_calls, [])
        self.assertIsNone(parallel.context)
        self.assertEqual(parallel.context_dict, {})

        context = ParserRuleContext()
        parallel = Parallel(task_calls=[TaskCall()], context=context)
        self.assertEqual(parallel.task_calls, [TaskCall()])
        self.assertEqual(parallel.context, context)
        self.assertEqual(parallel.context_dict, {})
