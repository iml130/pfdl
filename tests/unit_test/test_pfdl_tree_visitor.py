# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains unit tests tests for the PFDLTreeVisitor class.

Only valid input is checked because invalid syntax should be filtered through the
Parser and Lexer beforehand.
"""

# standard libraries
import unittest
from unittest.mock import MagicMock, Mock
from unittest.mock import patch


# local sources
from pfdl_scheduler.validation.error_handler import ErrorHandler
from pfdl_scheduler.parser.PFDLParser import PFDLParser
from pfdl_scheduler.parser.PFDLParserVisitor import PFDLParserVisitor
from pfdl_scheduler.model.process import Process
from pfdl_scheduler.model.struct import Struct
from pfdl_scheduler.model.task import Task
from pfdl_scheduler.model.service import Service
from pfdl_scheduler.model.task_call import TaskCall
from pfdl_scheduler.model.condition import Condition
from pfdl_scheduler.model.counting_loop import CountingLoop
from pfdl_scheduler.model.while_loop import WhileLoop
from pfdl_scheduler.model.array import Array

from pfdl_scheduler.parser.PFDLParser import PFDLParser
from antlr4.Token import Token

from pfdl_scheduler.parser.pfdl_tree_visitor import (
    PFDLTreeVisitor,
    PRIMITIVE_DATATYPES,
    IN_KEY,
    OUT_KEY,
    START_TASK,
)

from antlr4 import ParserRuleContext


class DummyContext(ParserRuleContext):
    def __init__(self):
        self.children = []


class TestPFDLTreeVisitor(unittest.TestCase):
    def setUp(self) -> None:
        self.error_handler: ErrorHandler = ErrorHandler("", False)
        self.visitor: PFDLTreeVisitor = PFDLTreeVisitor(self.error_handler)

    def check_if_print_error_is_called(self, method, *args) -> None:
        """Runs the given method wiht the help of a mock object and checks if print error is called.

        Args:
            method: The method which should be tested.
            args: Variable amount of arguments for the method to be tested.
        """
        with patch.object(self.error_handler, "print_error") as mock:
            method(*args)
        mock.assert_called()

    def test_visit_program(self):
        mock_program_ctx = PFDLParser.ProgramContext(None)
        mock_struct_ctx = PFDLParser.StructContext(None)
        mock_task_ctx = PFDLParser.TaskContext(None)

        mock_program_ctx.children = [mock_struct_ctx, mock_task_ctx]

        struct = Struct("Struct")
        task = Task("Task")

        with patch.object(self.visitor, "visitStruct", return_value=struct) as mock:
            with patch.object(self.visitor, "visitTask", return_value=task) as mock_2:
                process = self.visitor.visitProgram(mock_program_ctx)
                self.assertIsInstance(process, Process)
                self.assertEqual(len(process.structs), 1)
                self.assertIn("Struct", process.structs)
                self.assertIsInstance(process.structs["Struct"], Struct)
                self.assertEqual(len(process.tasks), 1)
                self.assertIn("Task", process.tasks)
                self.assertIsInstance(process.tasks["Task"], Task)
        mock.assert_called_once()
        mock_2.assert_called_once()

        # struct and task with this name already exist
        mock_program_ctx.children = [mock_struct_ctx, mock_struct_ctx]
        with patch.object(self.visitor, "visitStruct", return_value=struct) as mock:
            self.check_if_print_error_is_called(self.visitor.visitProgram, mock_program_ctx)
        self.assertEqual(mock.call_count, 2)

        mock_program_ctx.children = [mock_task_ctx, mock_task_ctx]
        with patch.object(self.visitor, "visitTask", return_value=task) as mock:
            self.check_if_print_error_is_called(self.visitor.visitProgram, mock_program_ctx)
        self.assertEqual(mock.call_count, 2)

    def test_visit_struct(self):
        # create a mock Struct context with two variables
        mock_variable_definition_ctx1 = PFDLParser.Variable_definitionContext(None)
        mock_variable_definition_ctx2 = PFDLParser.Variable_definitionContext(None)
        mock_struct_ctx = PFDLParser.StructContext(None)
        mock_struct_ctx.children = [mock_variable_definition_ctx1, mock_variable_definition_ctx2]

        create_and_add_token(PFDLParser.STARTS_WITH_UPPER_C_STR, "Struct", mock_struct_ctx)

        with patch.object(
            self.visitor,
            "visitVariable_definition",
            MagicMock(
                side_effect=[
                    ("var1", "number"),
                    ("var2", Array("number")),
                ]
            ),
        ) as mock:
            # visit the mock Struct context
            struct = self.visitor.visitStruct(mock_struct_ctx)

            # assert that the correct Struct object was created
            self.assertIsInstance(struct, Struct)
            self.assertEqual(struct.name, "Struct")
            self.assertEqual(len(struct.attributes), 2)
            self.assertIn("var1", struct.attributes)
            self.assertEqual(struct.attributes["var1"], "number")
            self.assertIn("var2", struct.attributes)
            self.assertEqual(struct.attributes["var2"], Array("number"))

        self.assertEqual(mock.call_count, 2)

        # duplicate attributes
        with patch.object(
            self.visitor,
            "visitVariable_definition",
            MagicMock(
                side_effect=[
                    ("var1", "number"),
                    ("var1", "string"),
                ]
            ),
        ) as mock:
            self.check_if_print_error_is_called(self.visitor.visitStruct, mock_struct_ctx)
        self.assertEqual(mock.call_count, 2)

    def test_visit_task(self):

        mock_task_in_ctx = PFDLParser.Task_inContext(None)
        mock_task_out_ctx = PFDLParser.Task_outContext(None)
        mock_statement_ctx_1 = PFDLParser.StatementContext(None)
        mock_statement_ctx_2 = PFDLParser.StatementContext(None)

        mock_task_ctx = PFDLParser.TaskContext(None)
        mock_task_ctx.children = [
            mock_task_in_ctx,
            mock_task_out_ctx,
            mock_statement_ctx_1,
            mock_statement_ctx_2,
        ]

        create_and_add_token(PFDLParser.STARTS_WITH_LOWER_C_STR, "Task", mock_task_ctx)

        input_parameters = {"param_1": "number", "param_2": Array("number")}
        output_parameters = ["param_1", "param_2"]
        statement_1 = Service()
        statement_2 = Condition()

        with patch.object(
            self.visitor,
            "visitTask_in",
            MagicMock(side_effect=[input_parameters]),
        ) as mock:
            with patch.object(
                self.visitor,
                "visitTask_out",
                MagicMock(side_effect=[output_parameters]),
            ) as mock_2:
                with patch.object(
                    self.visitor,
                    "visitStatement",
                    MagicMock(side_effect=[statement_1, statement_2]),
                ) as mock_3:
                    # visit the mock Task context
                    task = self.visitor.visitTask(mock_task_ctx)

                    # assert that the correct Task object was created
                    self.assertIsInstance(task, Task)
                    self.assertEqual(task.name, "Task")
                    self.assertEqual(len(task.input_parameters), 2)
                    self.assertIn("param_1", task.input_parameters)
                    self.assertEqual(task.input_parameters["param_1"], "number")
                    self.assertIn("param_2", task.input_parameters)
                    self.assertEqual(task.input_parameters["param_2"], Array("number"))
                    self.assertEqual(len(task.output_parameters), 2)
                    self.assertEqual(task.output_parameters[0], "param_1")
                    self.assertEqual(task.output_parameters[1], "param_2")

    def test_visitParameter(self):
        parameter_context = PFDLParser.ParameterContext(None)
        create_and_add_token(PFDLParser.STARTS_WITH_LOWER_C_STR, "a string", parameter_context)

        value = self.visitor.visitParameter(parameter_context)
        self.assertEqual(value, "a string")

        attribute_access_context = PFDLParser.Attribute_accessContext(None)
        create_and_add_token(PFDLParser.STARTS_WITH_LOWER_C_STR, "attr_1", attribute_access_context)
        create_and_add_token(PFDLParser.DOT, ".", attribute_access_context)
        create_and_add_token(PFDLParser.STARTS_WITH_LOWER_C_STR, "attr_2", attribute_access_context)
        create_and_add_token(PFDLParser.DOT, ".", attribute_access_context)
        create_and_add_token(PFDLParser.STARTS_WITH_LOWER_C_STR, "attr_3", attribute_access_context)

        parameter_context = PFDLParser.ParameterContext(None)
        parameter_context.children = [attribute_access_context]
        value = self.visitor.visitParameter(parameter_context)
        self.assertEqual(value, ["attr_1", "attr_2", "attr_3"])

    def test_visitAttribute_access(self):
        attribute_access_context = PFDLParser.Attribute_accessContext(None)
        create_and_add_token(PFDLParser.STARTS_WITH_LOWER_C_STR, "attr_1", attribute_access_context)
        attr_list = self.visitor.visitAttribute_access(attribute_access_context)
        self.assertEqual(attr_list, ["attr_1"])

        attribute_access_context = PFDLParser.Attribute_accessContext(None)
        create_and_add_token(PFDLParser.STARTS_WITH_LOWER_C_STR, "attr_1", attribute_access_context)
        create_and_add_token(PFDLParser.DOT, ".", attribute_access_context)
        create_and_add_token(PFDLParser.STARTS_WITH_LOWER_C_STR, "attr_2", attribute_access_context)
        create_and_add_token(PFDLParser.DOT, ".", attribute_access_context)
        create_and_add_token(PFDLParser.STARTS_WITH_LOWER_C_STR, "attr_3", attribute_access_context)
        attr_list = self.visitor.visitAttribute_access(attribute_access_context)
        self.assertEqual(attr_list, ["attr_1", "attr_2", "attr_3"])

    def test_visitVariable_definition(self):
        variable_definition_context = PFDLParser.Variable_definitionContext(None)
        # without array
        variable_definition_context.children = [
            PFDLParser.PrimitiveContext(None),
        ]
        create_and_add_token(
            PFDLParser.STARTS_WITH_LOWER_C_STR, "variable", variable_definition_context
        )

        with patch.object(self.visitor, "visitPrimitive", return_value="number"):
            self.assertEqual(
                self.visitor.visitVariable_definition(variable_definition_context),
                ("variable", "number"),
            )

        # with array
        variable_definition_context.children = [
            PFDLParser.PrimitiveContext(None),
            PFDLParser.ArrayContext(None),
        ]
        create_and_add_token(
            PFDLParser.STARTS_WITH_LOWER_C_STR, "variable", variable_definition_context
        )
        with patch.object(self.visitor, "visitPrimitive", return_value="string"):
            # without length
            with patch.object(self.visitor, "visitArray", return_value=-1):
                self.assertEqual(
                    self.visitor.visitVariable_definition(variable_definition_context),
                    ("variable", Array("string")),
                )
            # with length
            with patch.object(self.visitor, "visitArray", return_value=10):
                array = Array("string")
                array.length = 10
                self.assertEqual(
                    self.visitor.visitVariable_definition(variable_definition_context),
                    ("variable", array),
                )
            # with invalid length (string)
            with patch.object(self.visitor, "visitArray", return_value="not a number"):
                self.assertEqual(
                    self.visitor.visitVariable_definition(variable_definition_context),
                    ("variable", Array("string")),
                )
                self.check_if_print_error_is_called(
                    self.visitor.visitVariable_definition, variable_definition_context
                )

    def test_visitPrimitive(self):
        primitive_context = PFDLParser.PrimitiveContext(None)
        create_and_add_token(PFDLParser.NUMBER_P, "number", primitive_context)
        struct_id = self.visitor.visitPrimitive(primitive_context)
        self.assertEqual(struct_id, "number")

        primitive_context = PFDLParser.PrimitiveContext(None)
        create_and_add_token(PFDLParser.STRING_P, "string", primitive_context)
        struct_id = self.visitor.visitPrimitive(primitive_context)
        self.assertEqual(struct_id, "string")

        primitive_context = PFDLParser.PrimitiveContext(None)
        create_and_add_token(PFDLParser.BOOLEAN_P, "boolean", primitive_context)
        struct_id = self.visitor.visitPrimitive(primitive_context)
        self.assertEqual(struct_id, "boolean")

        primitive_context = PFDLParser.PrimitiveContext(None)
        create_and_add_token(PFDLParser.STARTS_WITH_UPPER_C_STR, "Primitive", primitive_context)
        struct_id = self.visitor.visitPrimitive(primitive_context)
        self.assertEqual(struct_id, "Primitive")

    def test_visitValue(self):
        value_context = PFDLParser.ValueContext(None)
        create_and_add_token(PFDLParser.TRUE, "True", value_context)
        value = self.visitor.visitValue(value_context)
        self.assertEqual(value, "True")

        value_context = PFDLParser.ValueContext(None)
        create_and_add_token(PFDLParser.FALSE, "False", value_context)
        value = self.visitor.visitValue(value_context)
        self.assertEqual(value, "False")

        value_context = PFDLParser.ValueContext(None)
        create_and_add_token(PFDLParser.INTEGER, "5", value_context)
        value = self.visitor.visitValue(value_context)
        self.assertEqual(value, "5")

        value_context = PFDLParser.ValueContext(None)
        create_and_add_token(PFDLParser.FLOAT, "5.0", value_context)
        value = self.visitor.visitValue(value_context)
        self.assertEqual(value, "5.0")

        attribute_access_context = PFDLParser.Attribute_accessContext(None)
        create_and_add_token(PFDLParser.STARTS_WITH_LOWER_C_STR, "attr_1", attribute_access_context)
        create_and_add_token(PFDLParser.DOT, ".", attribute_access_context)
        create_and_add_token(PFDLParser.STARTS_WITH_LOWER_C_STR, "attr_2", attribute_access_context)
        create_and_add_token(PFDLParser.DOT, ".", attribute_access_context)
        create_and_add_token(PFDLParser.STARTS_WITH_LOWER_C_STR, "attr_3", attribute_access_context)

        value_context = PFDLParser.ValueContext(None)
        value_context.children = [attribute_access_context]
        value = self.visitor.visitValue(value_context)
        self.assertEqual(value, ["attr_1", "attr_2", "attr_3"])

    def test_get_content(self):
        # create dummy context
        mock = MagicMock()
        mock.getText.return_value = "test"

        with patch.object(self.visitor, "visit", return_value=None):
            self.assertEqual(self.visitor.get_content(mock), "test")
        with patch.object(self.visitor, "visit", return_value=mock):
            self.assertEqual(self.visitor.get_content(mock), mock)

    def test_visitArray(self):
        array_context = PFDLParser.ArrayContext(None)

        # array without defined length
        self.assertEqual(self.visitor.visitArray(array_context), -1)

        # array with defined length
        array_context = PFDLParser.ArrayContext(None)
        create_and_add_token(PFDLParser.INTEGER, "10", array_context)
        self.assertEqual(self.visitor.visitArray(array_context), 10)

        # array with index variable
        array_context = PFDLParser.ArrayContext(None)
        create_and_add_token(PFDLParser.STARTS_WITH_LOWER_C_STR, "i", array_context)
        self.assertEqual(self.visitor.visitArray(array_context), "i")

    def test_visitExpression(self):
        # case length = 0
        expression_context = PFDLParser.ExpressionContext(None)
        expression_context.children = []
        self.assertIsNone(self.visitor.visitExpression(expression_context))

        # case length = 1
        expression_context.children = [
            PFDLParser.ExpressionContext(None),
        ]
        with patch.object(
            PFDLTreeVisitor,
            "get_content",
            MagicMock(side_effect=[["test"], "10", "5.0", "true"]),
        ):
            self.assertEqual(self.visitor.visitExpression(expression_context), ["test"])
            self.assertEqual(self.visitor.visitExpression(expression_context), 10)
            self.assertEqual(self.visitor.visitExpression(expression_context), 5.0)
            self.assertEqual(self.visitor.visitExpression(expression_context), True)

        # case length = 2
        expression_context.children = [
            PFDLParser.UnOperationContext(None),
            PFDLParser.ExpressionContext(None),
        ]

        with patch.object(
            PFDLTreeVisitor,
            "get_content",
            MagicMock(side_effect=["!", "value"]),
        ):
            expression = self.visitor.visitExpression(expression_context)
            self.assertEqual(len(expression), 2)
            self.assertTrue("unop" in expression)
            self.assertTrue("value" in expression)
            self.assertEqual(expression, {"unop": "!", "value": "value"})

        # case length = 3
        expression_context.children = [
            PFDLParser.ExpressionContext(None),
            PFDLParser.ExpressionContext(None),
            PFDLParser.ExpressionContext(None),
        ]

        with patch.object(
            PFDLTreeVisitor,
            "get_content",
            MagicMock(side_effect=["a", "And", "b"]),
        ):
            expression = self.visitor.visitExpression(expression_context)
            self.assertTrue("left" in expression)
            self.assertTrue("binOp" in expression)
            self.assertTrue("right" in expression)
            self.assertEqual(expression, {"left": "a", "binOp": "And", "right": "b"})

    def test_visitBinOperation(self):
        bin_op_context = PFDLParser.BinOperationContext(None)
        create_and_add_token(PFDLParser.LESS_THAN, "<", bin_op_context)
        bin_op = self.visitor.visitBinOperation(bin_op_context)
        self.assertEqual(bin_op, "<")

        bin_op_context = PFDLParser.BinOperationContext(None)
        create_and_add_token(PFDLParser.LESS_THAN_OR_EQUAL, "<=", bin_op_context)
        bin_op = self.visitor.visitBinOperation(bin_op_context)
        self.assertEqual(bin_op, "<=")

        bin_op_context = PFDLParser.BinOperationContext(None)
        create_and_add_token(PFDLParser.GREATER_THAN, ">", bin_op_context)
        bin_op = self.visitor.visitBinOperation(bin_op_context)
        self.assertEqual(bin_op, ">")

        bin_op_context = PFDLParser.BinOperationContext(None)
        create_and_add_token(PFDLParser.GREATER_THAN_OR_EQUAL, ">=", bin_op_context)
        bin_op = self.visitor.visitBinOperation(bin_op_context)
        self.assertEqual(bin_op, ">=")

        bin_op_context = PFDLParser.BinOperationContext(None)
        create_and_add_token(PFDLParser.EQUAL, "==", bin_op_context)
        bin_op = self.visitor.visitBinOperation(bin_op_context)
        self.assertEqual(bin_op, "==")

        bin_op_context = PFDLParser.BinOperationContext(None)
        create_and_add_token(PFDLParser.NOT_EQUAL, "!=", bin_op_context)
        bin_op = self.visitor.visitBinOperation(bin_op_context)
        self.assertEqual(bin_op, "!=")

        bin_op_context = PFDLParser.BinOperationContext(None)
        create_and_add_token(PFDLParser.STAR, "*", bin_op_context)
        bin_op = self.visitor.visitBinOperation(bin_op_context)
        self.assertEqual(bin_op, "*")

        bin_op_context = PFDLParser.BinOperationContext(None)
        create_and_add_token(PFDLParser.SLASH, "/", bin_op_context)
        bin_op = self.visitor.visitBinOperation(bin_op_context)
        self.assertEqual(bin_op, "/")

        bin_op_context = PFDLParser.BinOperationContext(None)
        create_and_add_token(PFDLParser.MINUS, "-", bin_op_context)
        bin_op = self.visitor.visitBinOperation(bin_op_context)
        self.assertEqual(bin_op, "-")

        bin_op_context = PFDLParser.BinOperationContext(None)
        create_and_add_token(PFDLParser.PLUS, "+", bin_op_context)
        bin_op = self.visitor.visitBinOperation(bin_op_context)
        self.assertEqual(bin_op, "+")

    def test_visitUnOperation(self):
        un_op_context = PFDLParser.UnOperationContext(None)
        create_and_add_token(PFDLParser.BOOLEAN_NOT, "!", un_op_context)
        un_op = self.visitor.visitUnOperation(un_op_context)
        self.assertEqual(un_op, "!")


def create_and_add_token(
    token_type: int, token_text: str, antlr_context: ParserRuleContext
) -> None:
    """Helper function to create a ANTLR Token object and to add
    it to the context object in one row."""
    token = Token()
    token.type = token_type
    token.text = token_text
    antlr_context.addTokenNode(token)
