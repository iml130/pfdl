# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains unit tests for the Process class."""

# standard libraries
import unittest

# local sources
from pfdl_scheduler.model.process import Process
from pfdl_scheduler.model.struct import Struct
from pfdl_scheduler.model.task import Task


class TestProcess(unittest.TestCase):
    """Tests for the methods of the Process class."""

    def test_init(self):
        process = Process()
        self.assertEqual(process.structs, {})
        self.assertEqual(process.tasks, {})

        process = Process(structs={"struct": Struct("struct_1")}, tasks={"task": Task()})
        self.assertEqual(process.structs, {"struct": Struct("struct_1")})
        self.assertEqual(process.tasks, {"task": Task()})
