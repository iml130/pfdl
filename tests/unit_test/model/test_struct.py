# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains unit tests tests for the Struct class and the 'parse_json' method."""

# standard libraries
import copy
import unittest

# local sources
from pfdl_scheduler.model.struct import Struct
from pfdl_scheduler.model.struct import parse_json
from pfdl_scheduler.model.array import Array
from pfdl_scheduler.validation.error_handler import ErrorHandler

# 3rd party libraries
from antlr4.ParserRuleContext import ParserRuleContext


class TestStruct(unittest.TestCase):
    """Tests for the methods of the Struct class."""

    def test_init(self):
        struct = Struct()
        self.assertEqual(struct.name, "")
        self.assertEqual(struct.attributes, {})
        self.assertIsNone(struct.context)
        self.assertEqual(struct.context_dict, {})

        attributes = {
            "attr1": "value",
            "attr2": Array([1, 2, 3]),
            "attr3": Struct(name="struct", attributes={"attr4": "value4"}),
        }

        context = ParserRuleContext()
        struct = Struct(name="struct", attributes=attributes, context=context)
        self.assertEqual(struct.name, "struct")
        self.assertEqual(struct.attributes, attributes)
        self.assertEqual(struct.context, context)
        self.assertEqual(struct.context_dict, {})

    def test_equal(self):
        struct1 = Struct(name="struct1", attributes={"attr1": "value1"})
        self.assertTrue(struct1 == struct1)

        struct2 = Struct(name="struct1", attributes={"attr1": "value1"})
        self.assertTrue(struct1 == struct2)

        struct3 = Struct(name="struct1", attributes={"attr1": "value2"})
        self.assertFalse(struct1 == struct3)

        struct4 = Struct(name="struct1", attributes={"attr1": Array(["value1"])})
        self.assertFalse(struct1 == struct4)

        self.assertFalse(struct1 == "struct1")

    def test_deep_copy(self):
        # do not test context, as we cant control the copying of it
        attributes = {"attr_1": "number", "attr2": Struct("struct2", {"attr_3": "string"})}
        struct = Struct("struct1", attributes, ParserRuleContext())
        copied_struct = copy.deepcopy(struct)

        self.assertEqual(copied_struct.name, "struct1")
        self.assertEqual(copied_struct.attributes, attributes)

    def test_struct_from_json(self):
        context = ParserRuleContext()

        json_string = '{"attr1": "value1", "attr2": [1, 2, 3], "attr3": {"attr4": "value4"}}'
        struct = Struct.from_json(json_string, ErrorHandler("", False), context)
        self.assertEqual(struct.name, "")

        attributes = {
            "attr1": "value1",
            "attr2": Array(values=[1, 2, 3], type_of_elements="number"),
            "attr3": Struct(attributes={"attr4": "value4"}, context=context),
        }
        self.assertEqual(struct.attributes, attributes)

        self.assertEqual(struct.context, context)
        self.assertEqual(struct.context_dict, {})

    def test_parse_json(self):
        context = ParserRuleContext()

        # empty
        struct = parse_json({}, ErrorHandler("", False), context)
        self.assertEqual(struct.name, "")
        self.assertEqual(struct.attributes, {})
        self.assertEqual(struct.context, context)
        self.assertEqual(struct.context_dict, {})

        # simple attributes
        attributes = {"attr1": "value1", "attr2": 123, "attr3": True}
        struct = parse_json(
            {"attr1": "value1", "attr2": 123, "attr3": True}, ErrorHandler("", False), context
        )
        self.assertEqual(struct.name, "")

        self.assertEqual(struct.attributes, attributes)
        self.assertEqual(struct.context, context)
        self.assertEqual(struct.context_dict, {})

        # nested struct
        struct_dict = {
            "attr1": 5,
            "attr2": [1, 2, 3],
            "attr3": {"attr4": "value4"},
            "attr5": {"attr6": ["str", "str_2"]},
            "attr7": {"attr8": {"attr9": True}},
            "attr10": [True, True, False],
        }
        struct = parse_json(struct_dict, ErrorHandler("", False), None)
        self.assertEqual(struct.name, "")
        self.assertEqual(
            struct.attributes,
            {
                "attr1": 5,
                "attr2": Array(values=[1, 2, 3], type_of_elements="number"),
                "attr3": Struct(name="", attributes={"attr4": "value4"}),
                "attr5": Struct(
                    name="",
                    attributes={"attr6": Array(values=["str", "str_2"], type_of_elements="string")},
                ),
                "attr7": Struct(
                    name="", attributes={"attr8": Struct(name="", attributes={"attr9": True})}
                ),
                "attr10": Array(values=[True, True, False], type_of_elements="boolean"),
            },
        )

        # structs in array
        struct_dict = {
            "attr1": [
                {
                    "attr2": 5,
                },
                {
                    "attr3": "string",
                },
            ]
        }
        struct = parse_json(struct_dict, ErrorHandler("", False), None)
        self.assertEqual(struct.name, "")
        array = Array("", [Struct("", {"attr2": 5}), Struct("", {"attr3": "string"})])
        self.assertEqual(struct.attributes, {"attr1": array})
