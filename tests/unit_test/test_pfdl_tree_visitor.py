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
from pfdl_scheduler.model.parallel import Parallel


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
        program_context = PFDLParser.ProgramContext(None)
        struct_context = PFDLParser.StructContext(None)
        task_context = PFDLParser.TaskContext(None)

        program_context.children = [struct_context, task_context]

        struct = Struct("Struct")
        task = Task("Task")

        with patch.object(self.visitor, "visitStruct", return_value=struct) as mock:
            with patch.object(self.visitor, "visitTask", return_value=task) as mock_2:
                process = self.visitor.visitProgram(program_context)
                self.assertIsInstance(process, Process)
                self.assertEqual(len(process.structs), 1)
                self.assertIn("Struct", process.structs)
                self.assertIsInstance(process.structs["Struct"], Struct)
                self.assertEqual(len(process.tasks), 1)
                self.assertIn("Task", process.tasks)
                self.assertIsInstance(process.tasks["Task"], Task)
        mock.assert_called_once_with(struct_context)
        mock_2.assert_called_once_with(task_context)

        # struct and task with this name already exist
        program_context.children = [struct_context, struct_context]
        with patch.object(self.visitor, "visitStruct", return_value=struct) as mock:
            self.check_if_print_error_is_called(self.visitor.visitProgram, program_context)
        self.assertEqual(mock.call_count, 2)

        program_context.children = [task_context, task_context]
        with patch.object(self.visitor, "visitTask", return_value=task) as mock:
            self.check_if_print_error_is_called(self.visitor.visitProgram, program_context)
        self.assertEqual(mock.call_count, 2)

    def test_visit_struct(self):
        variable_definition_context_1 = PFDLParser.Variable_definitionContext(None)
        variable_definition_context_2 = PFDLParser.Variable_definitionContext(None)
        struct_context = PFDLParser.StructContext(None)
        struct_context.children = [variable_definition_context_1, variable_definition_context_2]

        create_and_add_token(PFDLParser.STARTS_WITH_UPPER_C_STR, "Struct", struct_context)

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
            struct = self.visitor.visitStruct(struct_context)

            self.assertIsInstance(struct, Struct)
            self.assertEqual(struct.name, "Struct")
            self.assertEqual(struct.context, struct_context)
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
            self.check_if_print_error_is_called(self.visitor.visitStruct, struct_context)
        self.assertEqual(mock.call_count, 2)

    def test_visit_task(self):
        task_in_context = PFDLParser.Task_inContext(None)
        task_out_context = PFDLParser.Task_outContext(None)
        statement_context_1 = PFDLParser.StatementContext(None)
        statement_context_2 = PFDLParser.StatementContext(None)

        task_context = PFDLParser.TaskContext(None)
        task_context.children = [
            task_in_context,
            task_out_context,
            statement_context_1,
            statement_context_2,
        ]

        create_and_add_token(PFDLParser.STARTS_WITH_LOWER_C_STR, "Task", task_context)

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
                    task = self.visitor.visitTask(task_context)
                    self.assertIsInstance(task, Task)
                    self.assertEqual(task.name, "Task")
                    self.assertEqual(task.context, task_context)
                    self.assertEqual(len(task.input_parameters), 2)
                    self.assertIn("param_1", task.input_parameters)
                    self.assertEqual(task.input_parameters["param_1"], "number")
                    self.assertIn("param_2", task.input_parameters)
                    self.assertEqual(task.input_parameters["param_2"], Array("number"))
                    self.assertEqual(len(task.output_parameters), 2)
                    self.assertEqual(task.output_parameters[0], "param_1")
                    self.assertEqual(task.output_parameters[1], "param_2")

        mock.assert_called_once_with(task_in_context)
        mock_2.assert_called_once_with(task_out_context)
        mock_3.assert_called_with(statement_context_2)

    def test_visitTask_in(self):
        self.visitor.current_task = Task()

        task_in_context = PFDLParser.Task_inContext(None)
        task_in_context.children = [
            PFDLParser.Variable_definitionContext(None),
            PFDLParser.Variable_definitionContext(None),
        ]
        with patch.object(
            self.visitor,
            "visitVariable_definition",
            MagicMock(side_effect=[("var_1", "Struct_1"), ("var_2", "Struct_2")]),
        ):
            self.visitor.visitTask_in(task_in_context)

        # duplicate variable
        with patch.object(
            self.visitor,
            "visitVariable_definition",
            MagicMock(side_effect=[("var_1", "Struct_1"), ("var_1", "Struct_2")]),
        ):
            self.check_if_print_error_is_called(self.visitor.visitTask_in, task_in_context)

    def test_visitTask_out(self):
        task_out_context = PFDLParser.Task_outContext(None)
        create_and_add_token(PFDLParser.STARTS_WITH_LOWER_C_STR, "var_1", task_out_context)
        output_parameters = self.visitor.visitTask_out(task_out_context)

        self.assertEqual(len(output_parameters), 1)
        self.assertEqual(output_parameters[0], "var_1")

        task_out_context = PFDLParser.Task_outContext(None)
        create_and_add_token(PFDLParser.STARTS_WITH_LOWER_C_STR, "var_1", task_out_context)
        create_and_add_token(PFDLParser.STARTS_WITH_LOWER_C_STR, "var_2", task_out_context)
        create_and_add_token(PFDLParser.STARTS_WITH_LOWER_C_STR, "var_3", task_out_context)

        output_parameters = self.visitor.visitTask_out(task_out_context)
        self.assertEqual(len(output_parameters), 3)
        self.assertEqual(output_parameters[0], "var_1")
        self.assertEqual(output_parameters[1], "var_2")
        self.assertEqual(output_parameters[2], "var_3")

    def test_visitStatement(self):
        statement_context = PFDLParser.StatementContext(None)

        service_context = PFDLParser.Service_callContext(None)
        statement_context.children = [service_context]
        with patch.object(self.visitor, "visitService_call", return_value=Service()) as mock:
            self.assertIsInstance(self.visitor.visitStatement(statement_context), Service)
            mock.assert_called_once_with(service_context)

        task_call_context = PFDLParser.Task_callContext(None)
        statement_context.children = [task_call_context]
        with patch.object(self.visitor, "visitTask_call", return_value=TaskCall()) as mock:
            self.assertIsInstance(self.visitor.visitStatement(statement_context), TaskCall)
            mock.assert_called_once_with(task_call_context)

        parallel_context = PFDLParser.ParallelContext(None)
        statement_context.children = [parallel_context]
        with patch.object(self.visitor, "visitParallel", return_value=Parallel()) as mock:
            self.assertIsInstance(self.visitor.visitStatement(statement_context), Parallel)
            mock.assert_called_once_with(parallel_context)

        while_loop_context = PFDLParser.While_loopContext(None)
        statement_context.children = [while_loop_context]
        with patch.object(self.visitor, "visitWhile_loop", return_value=WhileLoop()) as mock:
            self.assertIsInstance(self.visitor.visitStatement(statement_context), WhileLoop)
            mock.assert_called_once_with(while_loop_context)

        counting_loop_context = PFDLParser.Counting_loopContext(None)
        statement_context.children = [counting_loop_context]
        with patch.object(self.visitor, "visitCounting_loop", return_value=CountingLoop()) as mock:
            self.assertIsInstance(self.visitor.visitStatement(statement_context), CountingLoop)
            mock.assert_called_once_with(counting_loop_context)

        condition_context = PFDLParser.ConditionContext(None)
        statement_context.children = [condition_context]
        with patch.object(self.visitor, "visitCondition", return_value=Condition()) as mock:
            self.assertIsInstance(self.visitor.visitStatement(statement_context), Condition)
            mock.assert_called_once_with(condition_context)

    def test_visitService_call(self):
        service_context = PFDLParser.Service_callContext(None)

        input_context = PFDLParser.Call_inputContext(None)
        output_context = PFDLParser.Call_outputContext(None)

        service_context.children = [input_context, output_context]
        create_and_add_token(PFDLParser.STARTS_WITH_UPPER_C_STR, "Service", service_context)

        struct = Struct()
        array = Array("Struct_2")

        with patch.object(
            self.visitor, "visitCall_input", return_value=["input_1", ["a", "b"], struct]
        ) as mock:
            with patch.object(
                self.visitor, "visitCall_output", return_value={"o1": "Struct", "o2": array}
            ) as mock_2:
                service = self.visitor.visitService_call(service_context)
                self.assertEqual(service.name, "Service")
                self.assertEqual(service.context, service_context)
                self.assertEqual(len(service.input_parameters), 3)
                self.assertEqual(service.input_parameters[0], "input_1")
                self.assertEqual(service.input_parameters[1], ["a", "b"])
                self.assertEqual(service.input_parameters[2], struct)
                self.assertEqual(len(service.output_parameters), 2)
                self.assertTrue("o1" in service.output_parameters)
                self.assertEqual(service.output_parameters["o1"], "Struct")
                self.assertTrue("o2" in service.output_parameters)
                self.assertEqual(service.output_parameters["o2"], array)

        mock.assert_called_once_with(input_context)
        mock_2.assert_called_once_with(output_context)

    def test_visitCall_input(self):
        call_input_context = PFDLParser.Call_inputContext(None)
        parameter_context_1 = PFDLParser.ParameterContext(None)
        parameter_context_2 = PFDLParser.ParameterContext(None)
        struct_init_context_1 = PFDLParser.Struct_initializationContext(None)
        struct_init_context_2 = PFDLParser.Struct_initializationContext(None)

        call_input_context.children = [
            parameter_context_1,
            parameter_context_2,
            struct_init_context_1,
            struct_init_context_2,
        ]

        struct_1 = Struct("Struct_1")
        struct_2 = Struct("Struct_2")

        with patch.object(
            self.visitor,
            "visitParameter",
            MagicMock(side_effect=["input", ["a", "b"]]),
        ) as mock:
            with patch.object(
                self.visitor,
                "visitStruct_initialization",
                MagicMock(side_effect=[struct_1, struct_2]),
            ) as mock_2:
                input_parameters = self.visitor.visitCall_input(call_input_context)
                self.assertEqual(len(input_parameters), 4)
                self.assertEqual(input_parameters[0], "input")
                self.assertEqual(input_parameters[1], ["a", "b"])
                self.assertEqual(input_parameters[2], struct_1)
                self.assertEqual(input_parameters[3], struct_2)

        mock.assert_called_with(parameter_context_2)
        mock_2.assert_called_with(struct_init_context_2)

    def test_visitCall_output(self):
        call_output_context = PFDLParser.Call_outputContext(None)
        variable_definition_context_1 = PFDLParser.Variable_definitionContext(None)
        variable_definition_context_2 = PFDLParser.Variable_definitionContext(None)

        call_output_context.children = [
            variable_definition_context_1,
            variable_definition_context_2,
        ]

        self.visitor.current_task = Task()

        with patch.object(
            self.visitor,
            "visitVariable_definition",
            MagicMock(side_effect=[("o1", "Struct_1"), ("o2", "Struct_2")]),
        ) as mock:
            output_parameters = self.visitor.visitCall_output(call_output_context)
            self.assertEqual(len(output_parameters), 2)
            self.assertTrue("o1" in output_parameters)
            self.assertEqual(output_parameters["o1"], "Struct_1")
            self.assertTrue("o2" in output_parameters)
            self.assertEqual(output_parameters["o2"], "Struct_2")

        mock.assert_called_with(variable_definition_context_2)

        # duplicate parameter
        with patch.object(
            self.visitor,
            "visitVariable_definition",
            MagicMock(side_effect=[("o1", "Struct_1"), ("o1", "Struct_2")]),
        ) as mock:
            self.check_if_print_error_is_called(self.visitor.visitCall_output, call_output_context)

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

    def test_visitStruct_initialization(self):
        struct_init_context = PFDLParser.Struct_initializationContext(None)
        json_object_context = PFDLParser.Json_objectContext(None)
        json_object_string = '{"name": "red", "rgb": [255, 255, 255]}'

        struct_init_context.children = [json_object_context]
        create_and_add_token(PFDLParser.STARTS_WITH_UPPER_C_STR, "Struct", struct_init_context)

        with patch.object(json_object_context, "getText", return_value=json_object_string) as mock:
            struct = self.visitor.visitStruct_initialization(struct_init_context)
            self.assertEqual(struct.name, "Struct")
            self.assertEqual(struct.context, struct_init_context)
            self.assertEqual(len(struct.attributes), 2)
            self.assertTrue("name" in struct.attributes)
            self.assertEqual(struct.attributes["name"], "red")
            self.assertTrue("rgb" in struct.attributes)
            self.assertEqual(struct.attributes["rgb"], Array("number", [255, 255, 255]))

        mock.assert_called_once()

    def test_visitTask_call(self):
        task_call_context = PFDLParser.Task_callContext(None)
        input_context = PFDLParser.Call_inputContext(None)
        output_context = PFDLParser.Call_outputContext(None)

        task_call_context.children = [input_context, output_context]
        create_and_add_token(PFDLParser.STARTS_WITH_LOWER_C_STR, "Task", task_call_context)

        struct = Struct()
        array = Array("Struct_2")
        with patch.object(
            self.visitor, "visitCall_input", return_value=["input_1", ["a", "b"], struct]
        ) as mock:
            with patch.object(
                self.visitor, "visitCall_output", return_value={"o1": "Struct", "o2": array}
            ) as mock_2:
                task_call = self.visitor.visitTask_call(task_call_context)
                self.assertEqual(task_call.name, "Task")
                self.assertEqual(task_call.context, task_call_context)
                self.assertEqual(len(task_call.input_parameters), 3)
                self.assertEqual(task_call.input_parameters[0], "input_1")
                self.assertEqual(task_call.input_parameters[1], ["a", "b"])
                self.assertEqual(task_call.input_parameters[2], struct)
                self.assertEqual(len(task_call.output_parameters), 2)
                self.assertTrue("o1" in task_call.output_parameters)
                self.assertEqual(task_call.output_parameters["o1"], "Struct")
                self.assertTrue("o2" in task_call.output_parameters)
                self.assertEqual(task_call.output_parameters["o2"], array)
                self.assertTrue(IN_KEY in task_call.context_dict)
                self.assertEqual(task_call.context_dict[IN_KEY], input_context)
                self.assertTrue(OUT_KEY in task_call.context_dict)
                self.assertEqual(task_call.context_dict[OUT_KEY], output_context)

        mock.assert_called_once_with(input_context)
        mock_2.assert_called_once_with(output_context)

    def test_visitParallel(self):
        parallel_context = PFDLParser.ParallelContext(None)
        task_call_context_1 = PFDLParser.Task_callContext(None)
        task_call_context_2 = PFDLParser.Task_callContext(None)
        parallel_context.children = [task_call_context_1, task_call_context_2]

        task_call_1 = TaskCall()
        task_call_2 = TaskCall()

        with patch.object(
            self.visitor, "visitTask_call", MagicMock(side_effect=[task_call_1, task_call_2])
        ) as mock:
            parallel = self.visitor.visitParallel(parallel_context)
            self.assertEqual(len(parallel.task_calls), 2)
            self.assertEqual(parallel.task_calls[0], task_call_1)
            self.assertEqual(parallel.task_calls[1], task_call_2)
            self.assertEqual(parallel.context, parallel_context)

        mock.assert_called_with(task_call_context_2)

    def test_visitWhileLoop(self):
        while_loop_context = PFDLParser.While_loopContext(None)
        expression_context = PFDLParser.ExpressionContext(None)
        statement_context_1 = PFDLParser.StatementContext(None)
        statement_context_2 = PFDLParser.StatementContext(None)

        while_loop_context.children = [expression_context, statement_context_1, statement_context_2]
        service = Service()
        condition = Condition()

        expression = {"unop": "!", "value": "True"}
        with patch.object(self.visitor, "visitExpression", return_value=expression) as mock:
            with patch.object(
                self.visitor, "visitStatement", MagicMock(side_effect=[service, condition])
            ) as mock_2:
                while_loop = self.visitor.visitWhile_loop(while_loop_context)
                self.assertEqual(while_loop.expression, expression)
                self.assertEqual(len(while_loop.statements), 2)
                self.assertEqual(while_loop.statements[0], service)
                self.assertEqual(while_loop.statements[1], condition)
                self.assertEqual(while_loop.context, while_loop_context)

        mock.assert_called_once_with(expression_context)
        mock_2.assert_called_with(statement_context_2)

    def test_visitCountingLoop(self):
        counting_loop_context = PFDLParser.Counting_loopContext(None)
        statement_context_1 = PFDLParser.StatementContext(None)
        statement_context_2 = PFDLParser.StatementContext(None)
        attribute_access_context = PFDLParser.Attribute_accessContext(None)
        counting_loop_context.children = [
            attribute_access_context,
            statement_context_1,
            statement_context_2,
        ]
        create_and_add_token(PFDLParser.STARTS_WITH_LOWER_C_STR, "i", counting_loop_context)

        service = Service()
        condition = Condition()

        # without parallel
        with patch.object(self.visitor, "visitAttribute_access", return_value=["a", "b"]) as mock:
            with patch.object(
                self.visitor, "visitStatement", MagicMock(side_effect=[service, condition])
            ) as mock_2:
                counting_loop = self.visitor.visitCounting_loop(counting_loop_context)
                self.assertEqual(counting_loop.counting_variable, "i")
                self.assertEqual(counting_loop.limit, ["a", "b"])
                self.assertFalse(counting_loop.parallel)
                self.assertEqual(len(counting_loop.statements), 2)
                self.assertEqual(counting_loop.statements[0], service)
                self.assertEqual(counting_loop.statements[1], condition)
                self.assertEqual(counting_loop.context, counting_loop_context)
        mock.assert_called_once_with(attribute_access_context)
        mock_2.assert_called_with(statement_context_2)

        # with parallel
        create_and_add_token(PFDLParser.PARALLEL, "Parallel", counting_loop_context)
        with patch.object(self.visitor, "visitAttribute_access", return_value=["a", "b"]) as mock:
            with patch.object(
                self.visitor, "visitStatement", MagicMock(side_effect=[service, condition])
            ) as mock_2:
                counting_loop = self.visitor.visitCounting_loop(counting_loop_context)
                self.assertEqual(counting_loop.counting_variable, "i")
                self.assertEqual(counting_loop.limit, ["a", "b"])
                self.assertTrue(counting_loop.parallel)
                self.assertEqual(len(counting_loop.statements), 2)
                self.assertEqual(counting_loop.statements[0], service)
                self.assertEqual(counting_loop.statements[1], condition)
                self.assertEqual(counting_loop.context, counting_loop_context)
        mock.assert_called_once_with(attribute_access_context)
        mock_2.assert_called_with(statement_context_2)

    def test_visitCondition(self):
        condition_context = PFDLParser.ConditionContext(None)
        expression_context = PFDLParser.ExpressionContext(None)
        condition_passed_context = PFDLParser.Condition_passedContext(None)

        condition_context.children = [expression_context, condition_passed_context]
        service = Service()
        while_loop = WhileLoop()
        counting_loop = CountingLoop()

        passed_statements = [service, while_loop]

        expression = {"unop": "!", "value": "True"}

        # without failed
        with patch.object(self.visitor, "visitExpression", return_value=expression) as mock:
            with patch.object(
                self.visitor, "visitCondition_passed", return_value=passed_statements
            ) as mock_2:
                condition = self.visitor.visitCondition(condition_context)
                self.assertEqual(condition.expression, expression)
                self.assertEqual(len(condition.passed_stmts), 2)
                self.assertEqual(condition.passed_stmts[0], service)
                self.assertEqual(condition.passed_stmts[1], while_loop)

        mock.assert_called_once_with(expression_context)
        mock_2.assert_called_once_with(condition_passed_context)

        condition_failed_context = PFDLParser.Condition_failedContext(None)
        condition_context.children = [
            expression_context,
            condition_passed_context,
            condition_failed_context,
        ]

        # with failed
        with patch.object(self.visitor, "visitExpression", return_value=expression) as mock:
            with patch.object(
                self.visitor, "visitCondition_passed", return_value=passed_statements
            ) as mock_2:
                with patch.object(
                    self.visitor, "visitCondition_failed", return_value=[counting_loop]
                ) as mock_3:
                    condition = self.visitor.visitCondition(condition_context)
                    self.assertEqual(condition.expression, expression)
                    self.assertEqual(len(condition.passed_stmts), 2)
                    self.assertEqual(condition.passed_stmts[0], service)
                    self.assertEqual(condition.passed_stmts[1], while_loop)
                    self.assertEqual(len(condition.failed_stmts), 1)
                    self.assertEqual(condition.failed_stmts[0], counting_loop)

        mock.assert_called_once_with(expression_context)
        mock_2.assert_called_once_with(condition_passed_context)
        mock_3.assert_called_once_with(condition_failed_context)

    def test_visitCondition_passed(self):
        condition_passed_context = PFDLParser.Condition_passedContext(None)
        statement_context_1 = PFDLParser.StatementContext(None)
        statement_context_2 = PFDLParser.StatementContext(None)

        condition_passed_context.children = [statement_context_1, statement_context_2]

        service = Service()
        while_loop = WhileLoop()

        with patch.object(
            self.visitor, "visitStatement", MagicMock(side_effect=[service, while_loop])
        ) as mock:
            statements = self.visitor.visitCondition_passed(condition_passed_context)
            self.assertEqual(len(statements), 2)
            self.assertEqual(statements[0], service)
            self.assertEqual(statements[1], while_loop)

        mock.assert_called_with(statement_context_2)

    def test_visitCondition_failed(self):
        condition_failed_context = PFDLParser.Condition_failedContext(None)
        statement_context_1 = PFDLParser.StatementContext(None)
        statement_context_2 = PFDLParser.StatementContext(None)

        condition_failed_context.children = [statement_context_1, statement_context_2]

        service = Service()
        while_loop = WhileLoop()

        with patch.object(
            self.visitor, "visitStatement", MagicMock(side_effect=[service, while_loop])
        ) as mock:
            statements = self.visitor.visitCondition_failed(condition_failed_context)
            self.assertEqual(len(statements), 2)
            self.assertEqual(statements[0], service)
            self.assertEqual(statements[1], while_loop)

        mock.assert_called_with(statement_context_2)

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

    def test_get_content(self):
        # create dummy context
        mock = MagicMock()
        mock.getText.return_value = "test"

        with patch.object(self.visitor, "visit", return_value=None):
            self.assertEqual(self.visitor.get_content(mock), "test")
        with patch.object(self.visitor, "visit", return_value=mock):
            self.assertEqual(self.visitor.get_content(mock), mock)

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
    """Helper function to create a ANTLR Token object and add it to the context object.

    This function has to be called after the children of a context are set, otherwise the
    results of this function are overwritten.

    Args:
        token_type: An integer or Token type in the PFDLParser representing the token.
        token_text: The text the token should be associated with.
        antlr_context: The context object this token should be added to.
    """
    token = Token()
    token.type = token_type
    token.text = token_text
    antlr_context.addTokenNode(token)
