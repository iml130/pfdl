# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""#TODO"""

# standard libraries
import unittest
from pfdl_scheduler.model.array import Array

# local sources
from pfdl_scheduler.parser.pfdl_tree_visitor import PFDLTreeVisitor

from pfdl_scheduler.parser.PFDLLexer import PFDLLexer
from pfdl_scheduler.parser.PFDLParser import PFDLParser

from pfdl_scheduler.model.process import Process
from pfdl_scheduler.model.struct import Struct
from pfdl_scheduler.model.task import Task

from antlr4.CommonTokenStream import CommonTokenStream
from antlr4.InputStream import InputStream

from pfdl_scheduler.validation.error_handler import ErrorHandler

test_programs = [
    # Simple Struct
    """
Struct Color
    name: string
    saturation: number
    rgb: number[3]
End

Struct CombinedColor
    color_1: Color
    color_2: Color
End

Struct RGBStrip
    colors: Color[]
End
""",
    # Simple Task
    """
Task paintTask
    Painting
        In
            Color
            {
                "name": "red",
                "saturation": 5,
                "rgb": [255, 255, 255]
            }
        Out
            pr_1: PaintResult
End
""",
]


class TestVisitor(unittest.TestCase):
    """
    Tests the methods of the PFDLTreeVisitor class.
    Run different PFDL programs and check if the output model
    has the correct data in it
    """

    def load_pfdl_file(self, index):
        lexer = PFDLLexer(InputStream(test_programs[index]))
        lexer.removeErrorListeners()

        token_stream = CommonTokenStream(lexer)

        parser = PFDLParser(token_stream)
        parser.removeErrorListeners()

        tree = parser.program()
        return tree

    def test_structs(self):
        tree = self.load_pfdl_file(0)
        error_handler = ErrorHandler("", used_in_extension=False)
        visitor = PFDLTreeVisitor(error_handler)
        process = visitor.visit(tree)

        self.assertEqual(len(process.structs), 3)
        self.assertTrue("Color" in process.structs, True)

        struct = process.structs["Color"]

        self.assertEqual(struct.name, "Color")
        self.assertEqual(len(struct.attributes), 3)

        self.assertTrue("name" in struct.attributes, True)
        self.assertEqual(struct.attributes["name"], "string")
        self.assertTrue("saturation" in struct.attributes, True)
        self.assertEqual(struct.attributes["saturation"], "number")
        self.assertTrue("rgb" in struct.attributes, True)
        self.assertTrue(isinstance(struct.attributes["rgb"], Array))
        array = struct.attributes["rgb"]
        self.assertEqual(array.type_of_elements, "number")
        self.assertEqual(array.length, 3)

        self.assertTrue("CombinedColor" in process.structs, True)
        struct = process.structs["CombinedColor"]
        self.assertEqual(struct.name, "CombinedColor")
        self.assertTrue("color_1" in struct.attributes, True)
        self.assertEqual(struct.attributes["color_1"], "Color")
        self.assertTrue("color_2" in struct.attributes, True)
        self.assertEqual(struct.attributes["color_2"], "Color")

        self.assertTrue("RGBStrip" in process.structs, True)
        struct = process.structs["RGBStrip"]
        self.assertEqual(struct.name, "RGBStrip")

        self.assertTrue("colors" in struct.attributes, True)
        self.assertTrue(isinstance(struct.attributes["colors"], Array))
        array = struct.attributes["colors"]
        self.assertEqual(array.type_of_elements, "Color")
        self.assertEqual(array.length, -1)  # undefined length

    def test_service_input_and_output(self):
        tree = self.load_pfdl_file(1)
        error_handler = ErrorHandler("", used_in_extension=False)
        visitor = PFDLTreeVisitor(error_handler)
        process = visitor.visit(tree)

    def test_task_call_input_and_output(self):
        pass
