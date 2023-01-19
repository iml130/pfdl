# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains unit tests for the Service class."""

# standard libraries
import unittest

# local sources
from pfdl_scheduler.model.service import Service
from pfdl_scheduler.model.struct import Struct

# 3rd party libraries
from antlr4.ParserRuleContext import ParserRuleContext


class TestService(unittest.TestCase):
    """Tests for the methods of the Service class."""

    def test_init(self):
        service = Service()
        self.assertEqual(service.name, "")
        self.assertEqual(service.input_parameters, [])
        self.assertEqual(service.output_parameters, {})
        self.assertIsNone(service.context)
        self.assertEqual(service.context_dict, {})

        struct = Struct(name="TestStruct")
        context = ParserRuleContext()
        service = Service(
            name="TestService",
            input_parameters=["input1", ["input2", "input3"], struct],
            output_parameters={"output1": "output1_type", "output2": ["output2_type"]},
            context=context,
        )
        self.assertEqual(service.name, "TestService")
        self.assertEqual(service.input_parameters, ["input1", ["input2", "input3"], struct])
        self.assertEqual(
            service.output_parameters, {"output1": "output1_type", "output2": ["output2_type"]}
        )
        self.assertIs(service.context, context)
        self.assertEqual(service.context_dict, {})
