# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains unit tests tests for the Scheduler class."""

# standard libraries
from pfdl_scheduler.model.condition import Condition
import unittest
from unittest.mock import MagicMixin, MagicMock, Mock, patch
from pfdl_scheduler.model import counting_loop

# local sources
from pfdl_scheduler.model.process import Process
from pfdl_scheduler.model.struct import Struct
from pfdl_scheduler.model.task import Task
from pfdl_scheduler.model.service import Service
from pfdl_scheduler.model.task_call import TaskCall
from pfdl_scheduler.model.while_loop import WhileLoop
from pfdl_scheduler.model.counting_loop import CountingLoop
from pfdl_scheduler.model.array import Array

from pfdl_scheduler.validation.error_handler import ErrorHandler
from pfdl_scheduler.validation.semantic_error_checker import SemanticErrorChecker


class DummyStart:
    def __init__(self):
        self.line = 0
        self.column = 0


class DummyContext:
    def __init__(self):
        self.start = DummyStart()


# ToDo: Check with mock objects if print error is called
class TestSemanticErrorChecker(unittest.TestCase):
    """
    Tests the methods of the SemanticErrorChecker
    Most methods will require a created Process object
    """

    def setUp(self):
        self.process = Process()
        self.error_handler = ErrorHandler("", False)
        self.checker = SemanticErrorChecker(self.error_handler, self.process)
        self.dummy_context = DummyContext()

    def test_init(self):
        structs = {"struct_1": Struct(), "struct_2": Struct()}
        tasks = {"task_1": Task(), "task_2": Task()}

        process = Process()
        process.structs = structs
        process.tasks = tasks
        semantic_error_checker = SemanticErrorChecker(None, process)

        self.assertEqual(semantic_error_checker.process, process)
        self.assertEqual(semantic_error_checker.structs, structs)
        self.assertEqual(semantic_error_checker.tasks, tasks)

    def test_check_structs(self):
        self.checker.structs = {
            "struct_1": Struct(),
            "struct_2": Struct(),
            "struct_3": Struct(),
        }
        with patch.object(self.checker, "check_for_unknown_datatypes_in_struct_definition") as mock:
            self.checker.check_structs()
        self.assertEqual(mock.call_count, 3)

    def test_check_for_unknown_datatypes_in_struct_definition(self):
        struct_definition = Struct()
        struct_definition.name = "Struct_1"

        struct_definition_2 = Struct()
        struct_definition_2.name = "Struct_2"

        self.process.structs[struct_definition.name] = struct_definition
        self.process.structs[struct_definition_2.name] = struct_definition_2

        struct_definition.attributes = {"identifier_1": "string"}
        check_result = self.checker.check_for_unknown_datatypes_in_struct_definition(
            struct_definition
        )
        self.assertTrue(check_result)

        struct_definition.attributes = {"identifier_1": "number"}
        check_result = self.checker.check_for_unknown_datatypes_in_struct_definition(
            struct_definition
        )
        self.assertTrue(check_result)

        struct_definition.attributes = {"identifier_1": "boolean"}
        check_result = self.checker.check_for_unknown_datatypes_in_struct_definition(
            struct_definition
        )
        self.assertTrue(check_result)

        array = Array()
        array.type_of_elements = "Struct_2"
        struct_definition.attributes = {"identifier_1": array}
        check_result = self.checker.check_for_unknown_datatypes_in_struct_definition(
            struct_definition
        )
        self.assertTrue(check_result)

        struct_definition.attributes = {"identifier_1": "Struct_2"}
        check_result = self.checker.check_for_unknown_datatypes_in_struct_definition(
            struct_definition
        )
        self.assertTrue(check_result)

        struct_definition.attributes = {"identifier_1": "unknown_datatype"}
        check_result = self.checker.check_for_unknown_datatypes_in_struct_definition(
            struct_definition
        )
        self.assertFalse(check_result)

        struct_definition.attributes = {"identifier_1": "Not_a_struct_name"}
        check_result = self.checker.check_for_unknown_datatypes_in_struct_definition(
            struct_definition
        )
        self.assertFalse(check_result)

        array.type_of_elements = "Not_a_struct_name"
        struct_definition.attributes = {"identifier_1": array}
        check_result = self.checker.check_for_unknown_datatypes_in_struct_definition(
            struct_definition
        )
        self.assertFalse(check_result)

    def test_check_tasks(self):
        self.checker.tasks = {"task_1": Task(), "task_2": Task()}

        # TODO: Search a better way to do this
        # Return value is set to false so it can be checked if the other methods are still executed
        with patch.object(self.checker, "check_statements", return_value=False) as mock_1:
            with patch.object(self.checker, "check_task_input_parameters") as mock_2:
                with patch.object(self.checker, "check_task_output_parameters") as mock_3:
                    self.checker.check_tasks()

        self.assertEqual(mock_1.call_count, 2)
        self.assertEqual(mock_2.call_count, 2)
        self.assertEqual(mock_3.call_count, 2)

    def test_check_statements(self):
        pass

    def test_check_statement(self):
        pass

    def test_check_task_input_parameters(self):
        pass

    def test_check_task_output_parameters(self):
        pass

    def test_check_on_done(self):
        pass

    def test_check_service(self):
        pass

    def test_check_task_call(self):
        pass

    def test_check_if_task_call_matches_with_called_task(self):
        pass

    def test_check_if_input_parameter_matches(self):
        pass

    def test_check_if_task_call_parameters_match(self):
        pass

    def test_check_call_parameters(self):
        task = Task()
        service = Service()
        service.input_parameters = ["test"]
        service.output_parameters = {"test": "test"}

        with patch.object(self.checker, "check_call_input_parameters") as input:
            with patch.object(self.checker, "check_call_output_parameters") as output:
                self.checker.check_call_parameters(service, task)
        input.assert_called_with(service, task)
        output.assert_called_with(service)

        service.output_parameters = {}

        with patch.object(self.checker, "check_call_input_parameters") as input:
            with patch.object(self.checker, "check_call_output_parameters") as output:
                self.checker.check_call_parameters(service, task)
        input.assert_called_with(service, task)
        output.assert_not_called()

        service.input_parameters = []
        service.output_parameters = {"test": "test"}

        with patch.object(self.checker, "check_call_input_parameters") as input:
            with patch.object(self.checker, "check_call_output_parameters") as output:
                self.checker.check_call_parameters(service, task)
        input.assert_not_called()
        output.assert_called_with(service)

        task_call = TaskCall()
        task_call.input_parameters = ["test"]
        task_call.output_parameters = {"test": "test"}

        with patch.object(self.checker, "check_call_input_parameters") as input:
            with patch.object(self.checker, "check_call_output_parameters") as output:
                self.checker.check_call_parameters(task_call, task)
        input.assert_called_with(task_call, task)
        output.assert_called_with(task_call)

    def test_check_call_input_parameters(self):
        pass

    def test_check_attribute_access(self):
        pass

    def test_check_call_output_parameters(self):
        pass

    def test_check_instantiated_struct_attributes(self):
        pass

    def test_check_if_struct_exists(self):
        self.checker.structs = {"Struct_1": Struct(), "Struct_2": Struct()}
        self.assertTrue(self.checker.check_if_struct_exists(Struct("Struct_1")))
        self.assertTrue(self.checker.check_if_struct_exists(Struct("Struct_2")))
        self.assertFalse(self.checker.check_if_struct_exists(Struct("Not_a_struct")))

    def test_check_for_unknown_attribute_in_struct(self):
        struct_definition = Struct("Test", {"identifier_1": "string", "identifier_2": "number"})
        instantiated_struct = Struct()

        # a struct variable which was instantiated in an service call, for example
        instantiated_struct.context_dict["identifier_1"] = DummyContext()
        instantiated_struct.context_dict["identifier_2"] = DummyContext()
        instantiated_struct.context_dict["unknown_identifier"] = DummyContext()

        self.assertTrue(
            self.checker.check_for_unknown_attribute_in_struct(
                instantiated_struct, "identifier_1", struct_definition
            )
        )
        self.assertTrue(
            self.checker.check_for_unknown_attribute_in_struct(
                instantiated_struct, "identifier_2", struct_definition
            )
        )
        self.assertFalse(
            self.checker.check_for_unknown_attribute_in_struct(
                instantiated_struct, "unknown_identifier", struct_definition
            )
        )

    # ToDo: Überarbeiten, Attribute liegen nun direkt mit korrekten Typen vor
    def test_check_for_wrong_attribute_type_in_struct(self):
        struct_definition = Struct()
        struct_definition.name = "Test"
        instantiated_struct = Struct()
        instantiated_struct.context_dict["identifier_1"] = DummyContext()

        # type is string
        struct_definition.attributes = {"identifier_1": "string"}
        instantiated_struct.attributes = {"identifier_1": "a string"}
        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "identifier_1", struct_definition
        )
        self.assertTrue(check_result)

        instantiated_struct.attributes = {"identifier_1": 5}
        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "identifier_1", struct_definition
        )
        self.assertFalse(check_result)

        instantiated_struct.attributes = {"identifier_1": Array()}
        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "identifier_1", struct_definition
        )
        self.assertFalse(check_result)

        instantiated_struct.attributes = {"identifier_1": True}
        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "identifier_1", struct_definition
        )
        self.assertFalse(check_result)

        instantiated_struct.attributes = {"identifier_1": Struct()}
        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "identifier_1", struct_definition
        )
        self.assertFalse(check_result)

        # type is number
        struct_definition.attributes = {"identifier_1": "number"}
        instantiated_struct.attributes = {"identifier_1": 5}
        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "identifier_1", struct_definition
        )
        self.assertTrue(check_result)

        instantiated_struct.attributes = {"identifier_1": "a string"}
        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "identifier_1", struct_definition
        )
        self.assertFalse(check_result)

        instantiated_struct.attributes = {"identifier_1": Array()}
        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "identifier_1", struct_definition
        )
        self.assertFalse(check_result)

        instantiated_struct.attributes = {"identifier_1": True}
        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "identifier_1", struct_definition
        )
        self.assertFalse(check_result)

        instantiated_struct.attributes = {"identifier_1": Struct()}
        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "identifier_1", struct_definition
        )
        self.assertFalse(check_result)

        # type is boolean
        struct_definition.attributes = {"identifier_1": "boolean"}
        instantiated_struct.attributes = {"identifier_1": True}
        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "identifier_1", struct_definition
        )
        self.assertTrue(check_result)

        instantiated_struct.attributes = {"identifier_1": "a string"}
        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "identifier_1", struct_definition
        )
        self.assertFalse(check_result)

        instantiated_struct.attributes = {"identifier_1": Array()}
        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "identifier_1", struct_definition
        )
        self.assertFalse(check_result)

        instantiated_struct.attributes = {"identifier_1": 5}
        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "identifier_1", struct_definition
        )
        self.assertFalse(check_result)

        instantiated_struct.attributes = {"identifier_1": Struct()}
        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "identifier_1", struct_definition
        )
        self.assertFalse(check_result)

        # type is Array
        struct_definition.attributes = {"identifier_1": Array()}
        instantiated_struct.attributes = {"identifier_1": Array()}
        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "identifier_1", struct_definition
        )
        self.assertTrue(check_result)

        instantiated_struct.attributes = {"identifier_1": "a string"}
        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "identifier_1", struct_definition
        )
        self.assertFalse(check_result)

        instantiated_struct.attributes = {"identifier_1": 5}
        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "identifier_1", struct_definition
        )
        self.assertFalse(check_result)

        instantiated_struct.attributes = {"identifier_1": True}
        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "identifier_1", struct_definition
        )
        self.assertFalse(check_result)

        instantiated_struct.attributes = {"identifier_1": Struct()}
        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "identifier_1", struct_definition
        )
        self.assertFalse(check_result)

        struct_definition.attributes = {"nested_struct": "NestedStruct_1"}
        struct_definition_2 = Struct()
        struct_definition_2.attributes = {"nested_struct": "NestedStruct_2"}
        struct_definition_3 = Struct()
        struct_definition_3.attributes = {"attribute": "string"}

        nested_struct = Struct()
        nested_struct.name = "NestedStruct_1"
        nested_struct_2 = Struct()
        nested_struct_2.name = "NestedStruct_2"

        instantiated_struct.attributes = {"nested_struct": nested_struct}
        nested_struct.attributes = {"nested_struct": nested_struct_2}
        nested_struct_2.attributes = {"attribute": '"a string"'}

        self.process.structs["NestedStruct_1"] = struct_definition_2
        self.process.structs["NestedStruct_2"] = struct_definition_3

        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "nested_struct", struct_definition
        )
        self.assertTrue(check_result)

        instantiated_struct.attributes = {"identifier_1": "not_a_struct_name"}

        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "identifier_1", struct_definition
        )
        self.assertFalse(check_result)

        instantiated_struct.attributes = {"identifier_1": '"a string"'}
        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "identifier_1", struct_definition
        )
        self.assertFalse(check_result)

        instantiated_struct.attributes = {"identifier_1": Array()}
        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "identifier_1", struct_definition
        )
        self.assertFalse(check_result)

        instantiated_struct.attributes = {"identifier_1": "True"}
        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "identifier_1", struct_definition
        )
        self.assertFalse(check_result)

        instantiated_struct.attributes = {"identifier_1": "5"}
        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "identifier_1", struct_definition
        )
        self.assertFalse(check_result)

    def test_check_for_missing_attribute_in_struct(self):
        struct_definition = Struct()
        struct_definition.name = "Test"
        instantiated_struct = Struct()
        instantiated_struct.context_dict["identifier_1"] = DummyContext()

        struct_definition.attributes = {"identifier_1": "string"}
        instantiated_struct.attributes = {"identifier_1": '"a string"'}

    # ToDo: Check with mock variables if statements are checked
    # Check if expressions are checked

    def test_check_while_loop(self):
        expression = {"True"}
        task = Task()

        while_loop = WhileLoop(expression=expression)
        while_loop.statements = [
            Service("service_1"),
            Service("service_2"),
            TaskCall("task_call"),
        ]

        with patch.object(self.checker, "check_statement") as mock_1:
            with patch.object(self.checker, "check_expression") as mock_2:
                self.checker.check_while_loop(while_loop, task)
        self.assertEqual(mock_1.call_count, 3)
        mock_2.assert_called_with(expression, None, task)

    def test_check_counting_loop(self):
        task = Task()

        counting_loop = CountingLoop()
        counting_loop.statements = [
            Service("service_1"),
            Service("service_2"),
            TaskCall("task_call"),
        ]

        with patch.object(self.checker, "check_statement") as mock:
            self.checker.check_counting_loop(counting_loop, task)
        self.assertEqual(mock.call_count, 3)

    def test_check_conditional_statement(self):
        expression = {"True"}
        task = Task()

        condition = Condition(expression=expression)
        condition.passed_stmts = [Service("service_1"), Service("service_2")]
        condition.failed_stmts = [TaskCall("task_call")]

        with patch.object(self.checker, "check_statement") as mock_1:
            with patch.object(self.checker, "check_expression") as mock_2:
                self.checker.check_conditional_statement(condition, task)
        self.assertEqual(mock_1.call_count, 3)
        mock_2.assert_called_with(expression, None, task)

    def test_check_expression(self):
        struct = Struct(
            "struct",
            {"attribute": "number", "attribute_2": "string", "attribute_3": "boolean"},
        )
        task = Task()
        task.variables = {"variable": "struct"}
        self.checker.structs = {"struct": struct}

        variable_list = ["variable", "attribute"]
        variable_list_2 = ["variable", "attribute_2"]
        variable_list_3 = ["variable", "attribute_3"]

        # Run all the testcases from the tests above for the expression check methods
        self.assertTrue(self.checker.check_expression(5, None, task))
        self.assertTrue(self.checker.check_expression(5.0, None, task))
        self.assertTrue(self.checker.check_expression(True, None, task))
        self.assertTrue(self.checker.check_expression(False, None, task))
        self.assertTrue(self.checker.check_expression(variable_list, None, task))
        self.assertTrue(self.checker.check_expression(variable_list_3, None, task))
        self.assertTrue(self.checker.check_expression("a_string", None, task))

        self.assertFalse(self.checker.check_expression(variable_list_2, None, task))

        self.assertTrue(
            self.checker.check_expression({"unop": "!", "value": variable_list}, None, task)
        )
        self.assertTrue(
            self.checker.check_expression({"unop": "!", "value": variable_list_3}, None, task)
        )

        expression = {
            "left": variable_list_3,
            "binOp": "Or",
            "right": {"left": 5, "binOp": "<", "right": variable_list},
        }
        self.assertTrue(
            self.checker.check_expression({"unop": "!", "value": expression}, None, task)
        )
        expression = {
            "left": variable_list_3,
            "binOp": "!=",
            "right": {"left": "(", "binOp": "true", "right": ")"},
        }
        self.assertTrue(
            self.checker.check_expression({"unop": "!", "value": expression}, None, task)
        )
        expression = {
            "left": variable_list_3,
            "binOp": "!=",
            "right": {
                "left": "(",
                "binOp": {"left": 5, "binOp": "<", "right": 10},
                "right": ")",
            },
        }
        self.assertTrue(
            self.checker.check_expression({"unop": "!", "value": expression}, None, task)
        )

        self.assertFalse(
            self.checker.check_expression({"unop": "!", "value": variable_list_2}, None, task)
        )
        expression = {
            "left": variable_list_2,
            "binOp": "Or",
            "right": {"left": 5, "binOp": "<", "right": variable_list},
        }
        self.assertFalse(
            self.checker.check_expression({"unop": "!", "value": expression}, None, task)
        )
        expression = {
            "left": variable_list_3,
            "binOp": "Or",
            "right": {"left": "True", "binOp": "<", "right": variable_list},
        }
        self.assertFalse(
            self.checker.check_expression({"unop": "!", "value": expression}, None, task)
        )
        expression = {
            "left": variable_list_3,
            "binOp": "!=",
            "right": {
                "left": "(",
                "binOp": {"left": 5, "binOp": "<", "right": variable_list_2},
                "right": ")",
            },
        }
        self.assertFalse(
            self.checker.check_expression({"unop": "!", "value": expression}, None, task)
        )

        self.assertTrue(
            self.checker.check_expression({"left": 5, "binOp": "<", "right": 10}, None, task)
        )
        self.assertTrue(
            self.checker.check_expression({"left": 5, "binOp": ">", "right": 10}, None, task)
        )
        self.assertTrue(
            self.checker.check_expression({"left": 5, "binOp": "<=", "right": 10}, None, task)
        )
        self.assertTrue(
            self.checker.check_expression({"left": 5, "binOp": ">=", "right": 10}, None, task)
        )
        self.assertTrue(
            self.checker.check_expression({"left": "a", "binOp": "<", "right": "b"}, None, task)
        )
        self.assertTrue(
            self.checker.check_expression({"left": True, "binOp": "==", "right": True}, None, task)
        )
        self.assertTrue(
            self.checker.check_expression({"left": True, "binOp": "==", "right": 1}, None, task)
        )
        self.assertTrue(
            self.checker.check_expression(
                {"left": variable_list, "binOp": "<", "right": 1}, None, task
            )
        )
        self.assertTrue(
            self.checker.check_expression(
                {"left": True, "binOp": "And", "right": False}, None, task
            )
        )
        self.assertTrue(
            self.checker.check_expression(
                {"left": variable_list_3, "binOp": "==", "right": False}, None, task
            )
        )
        self.assertTrue(
            self.checker.check_expression(
                {"left": variable_list_3, "binOp": "==", "right": 1}, None, task
            )
        )

        expression = {
            "left": variable_list_3,
            "binOp": "Or",
            "right": {"left": 5, "binOp": "<", "right": variable_list},
        }
        self.assertTrue(self.checker.check_expression(expression, None, task))
        expression = {
            "left": variable_list_3,
            "binOp": "!=",
            "right": {"left": "(", "binOp": True, "right": ")"},
        }
        self.assertTrue(self.checker.check_expression(expression, None, task))
        expression = {
            "left": variable_list_3,
            "binOp": "!=",
            "right": {
                "left": "(",
                "binOp": {"left": 5, "binOp": "<", "right": 10},
                "right": ")",
            },
        }
        self.assertTrue(self.checker.check_expression(expression, None, task))

        self.assertFalse(
            self.checker.check_expression(
                {"left": 5, "binOp": "<", "right": "a_string"}, None, task
            )
        )
        self.assertFalse(
            self.checker.check_expression(
                {"left": variable_list_2, "binOp": "<", "right": 1}, None, task
            )
        )
        self.assertFalse(
            self.checker.check_expression(
                {"left": variable_list_3, "binOp": "<", "right": 1}, None, task
            )
        )

        expression = {
            "left": variable_list_2,
            "binOp": "Or",
            "right": {"left": 5, "binOp": "<", "right": variable_list},
        }
        self.assertFalse(self.checker.check_expression(expression, None, task))

        # boolean or boolean < number -> valid
        expression = {
            "left": variable_list_3,
            "binOp": "Or",
            "right": {"left": True, "binOp": "<", "right": variable_list},
        }
        self.assertTrue(self.checker.check_expression(expression, None, task))

        expression = {
            "left": variable_list_3,
            "binOp": "!=",
            "right": {
                "left": "(",
                "binOp": {"left": 5, "binOp": "<", "right": variable_list_2},
                "right": ")",
            },
        }
        self.assertFalse(self.checker.check_expression(expression, None, task))

    def test_check_single_expression(self):
        struct = Struct()
        struct.name = "struct"
        struct.attributes = {
            "attribute": "number",
            "attribute_2": "string",
            "attribute_3": "boolean",
        }
        task = Task()
        task.variables = {"variable": "struct"}
        self.checker.structs = {"struct": struct}

        variable_list = ["variable", "attribute"]
        variable_list_2 = ["variable", "attribute_2"]
        variable_list_3 = ["variable", "attribute_3"]

        self.assertTrue(self.checker.check_single_expression(5, None, task))
        self.assertTrue(self.checker.check_single_expression(5.0, None, task))
        self.assertTrue(self.checker.check_single_expression(True, None, task))
        self.assertTrue(self.checker.check_single_expression(False, None, task))
        self.assertTrue(self.checker.check_single_expression(variable_list, None, task))
        self.assertTrue(self.checker.check_single_expression(variable_list_3, None, task))
        self.assertTrue(self.checker.check_single_expression("a_string", None, task))

        self.assertFalse(self.checker.check_single_expression(variable_list_2, None, task))

    def test_check_unary_operation(self):
        struct = Struct()
        struct.name = "struct"
        struct.attributes = {
            "attribute": "number",
            "attribute_2": "string",
            "attribute_3": "boolean",
        }
        task = Task()
        task.variables = {"variable": "struct"}
        self.checker.structs = {"struct": struct}

        variable_list = ["variable", "attribute"]
        variable_list_2 = ["variable", "attribute_2"]
        variable_list_3 = ["variable", "attribute_3"]

        self.assertTrue(
            self.checker.check_unary_operation({"unop": "!", "value": variable_list}, None, task)
        )
        self.assertTrue(
            self.checker.check_unary_operation({"unop": "!", "value": variable_list_3}, None, task)
        )

        expression = {
            "left": variable_list_3,
            "binOp": "Or",
            "right": {"left": 5, "binOp": "<", "right": variable_list},
        }
        self.assertTrue(
            self.checker.check_unary_operation({"unop": "!", "value": expression}, None, task)
        )
        expression = {
            "left": variable_list_3,
            "binOp": "!=",
            "right": {"left": "(", "binOp": "true", "right": ")"},
        }
        self.assertTrue(
            self.checker.check_unary_operation({"unop": "!", "value": expression}, None, task)
        )
        expression = {
            "left": variable_list_3,
            "binOp": "!=",
            "right": {
                "left": "(",
                "binOp": {"left": 5, "binOp": "<", "right": 10},
                "right": ")",
            },
        }
        self.assertTrue(
            self.checker.check_unary_operation({"unop": "!", "value": expression}, None, task)
        )

        self.assertFalse(
            self.checker.check_unary_operation({"unop": "!", "value": variable_list_2}, None, task)
        )
        expression = {
            "left": variable_list_2,
            "binOp": "Or",
            "right": {"left": 5, "binOp": "<", "right": variable_list},
        }
        self.assertFalse(
            self.checker.check_unary_operation({"unop": "!", "value": expression}, None, task)
        )
        expression = {
            "left": variable_list_3,
            "binOp": "Or",
            "right": {"left": "True", "binOp": "<", "right": variable_list},
        }
        self.assertFalse(
            self.checker.check_unary_operation({"unop": "!", "value": expression}, None, task)
        )
        expression = {
            "left": variable_list_3,
            "binOp": "!=",
            "right": {
                "left": "(",
                "binOp": {"left": 5, "binOp": "<", "right": variable_list_2},
                "right": ")",
            },
        }
        self.assertFalse(
            self.checker.check_unary_operation({"unop": "!", "value": expression}, None, task)
        )

    def test_check_binary_operation(self):
        struct = Struct()
        struct.name = "struct"
        struct.attributes = {
            "attribute": "number",
            "attribute_2": "string",
            "attribute_3": "boolean",
        }
        task = Task()
        task.variables = {"variable": "struct"}
        self.checker.structs = {"struct": struct}

        variable_list = ["variable", "attribute"]
        variable_list_2 = ["variable", "attribute_2"]
        variable_list_3 = ["variable", "attribute_3"]

        self.assertTrue(
            self.checker.check_binary_operation({"left": 5, "binOp": "<", "right": 10}, None, task)
        )
        self.assertTrue(
            self.checker.check_binary_operation({"left": 5, "binOp": ">", "right": 10}, None, task)
        )
        self.assertTrue(
            self.checker.check_binary_operation({"left": 5, "binOp": "<=", "right": 10}, None, task)
        )
        self.assertTrue(
            self.checker.check_binary_operation({"left": 5, "binOp": ">=", "right": 10}, None, task)
        )
        self.assertTrue(
            self.checker.check_binary_operation(
                {"left": "a", "binOp": "<", "right": "b"}, None, task
            )
        )
        self.assertTrue(
            self.checker.check_binary_operation(
                {"left": True, "binOp": "==", "right": True}, None, task
            )
        )
        self.assertTrue(
            self.checker.check_binary_operation(
                {"left": True, "binOp": "==", "right": 1}, None, task
            )
        )
        self.assertTrue(
            self.checker.check_binary_operation(
                {"left": variable_list, "binOp": "<", "right": 1}, None, task
            )
        )
        self.assertTrue(
            self.checker.check_binary_operation(
                {"left": True, "binOp": "And", "right": False}, None, task
            )
        )
        self.assertTrue(
            self.checker.check_binary_operation(
                {"left": variable_list_3, "binOp": "==", "right": False}, None, task
            )
        )
        self.assertTrue(
            self.checker.check_binary_operation(
                {"left": variable_list_3, "binOp": "==", "right": 1}, None, task
            )
        )

        expression = {
            "left": variable_list_3,
            "binOp": "Or",
            "right": {"left": 5, "binOp": "<", "right": variable_list},
        }
        self.assertTrue(self.checker.check_binary_operation(expression, None, task))
        expression = {
            "left": variable_list_3,
            "binOp": "!=",
            "right": {"left": "(", "binOp": True, "right": ")"},
        }
        self.assertTrue(self.checker.check_binary_operation(expression, None, task))
        expression = {
            "left": variable_list_3,
            "binOp": "!=",
            "right": {
                "left": "(",
                "binOp": {"left": 5, "binOp": "<", "right": 10},
                "right": ")",
            },
        }
        self.assertTrue(self.checker.check_binary_operation(expression, None, task))

        self.assertFalse(
            self.checker.check_binary_operation(
                {"left": 5, "binOp": "<", "right": "a_string"}, None, task
            )
        )
        self.assertFalse(
            self.checker.check_binary_operation(
                {"left": variable_list_2, "binOp": "<", "right": 1}, None, task
            )
        )
        self.assertFalse(
            self.checker.check_binary_operation(
                {"left": variable_list_3, "binOp": "<", "right": 1}, None, task
            )
        )

        expression = {
            "left": variable_list_2,
            "binOp": "Or",
            "right": {"left": 5, "binOp": "<", "right": variable_list},
        }
        self.assertFalse(self.checker.check_binary_operation(expression, None, task))

        # boolean or boolean < number -> valid
        expression = {
            "left": variable_list_3,
            "binOp": "Or",
            "right": {"left": True, "binOp": "<", "right": variable_list},
        }
        self.assertTrue(self.checker.check_binary_operation(expression, None, task))
        expression = {
            "left": variable_list_3,
            "binOp": "!=",
            "right": {
                "left": "(",
                "binOp": {"left": 5, "binOp": "<", "right": variable_list_2},
                "right": ")",
            },
        }
        self.assertFalse(self.checker.check_binary_operation(expression, None, task))

    def test_expression_is_number(self):
        struct = Struct()
        struct.name = "struct"
        struct.attributes = {"attribute": "number", "attribute_2": "string"}
        task = Task()
        task.variables = {"variable": "struct"}
        self.checker.structs = {"struct": struct}

        variable_list = ["variable", "attribute"]
        variable_list_2 = ["variable", "attribute_2"]

        self.assertTrue(self.checker.expression_is_number(5, task))
        self.assertTrue(self.checker.expression_is_number(10.0, task))
        self.assertTrue(self.checker.expression_is_number(variable_list, task))
        self.assertTrue(self.checker.expression_is_number(True, task))

        self.assertFalse(self.checker.expression_is_number("a string", task))
        self.assertFalse(self.checker.expression_is_number(variable_list_2, task))

    def test_expression_is_string(self):
        struct = Struct()
        struct.name = "struct"
        struct.attributes = {"attribute": "string", "attribute_2": "number"}
        task = Task()
        task.variables = {"variable": "struct"}
        self.checker.structs = {"struct": struct}

        variable_list = ["variable", "attribute"]
        variable_list_2 = ["variable", "attribute_2"]

        self.assertTrue(self.checker.expression_is_string("a string", None))
        self.assertTrue(self.checker.expression_is_string("6", None))
        self.assertTrue(self.checker.expression_is_string("True", None))
        self.assertTrue(self.checker.expression_is_string(variable_list, task))

        self.assertFalse(self.checker.expression_is_string(5, None))
        self.assertFalse(self.checker.expression_is_string(True, None))
        self.assertFalse(self.checker.expression_is_string(variable_list_2, task))

    def test_check_if_variable_definition_is_valid(self):
        self.checker.structs = {"Struct_1": Struct(), "Struct_2": Struct()}
        array_1 = Array("Struct_1")
        array_2 = Array("Struct_2")
        array_3 = Array("number")
        array_4 = Array("Not_a_struct")
        array_5 = Array("not_a_primitive_datatype")

        self.assertTrue(
            self.checker.check_if_variable_definition_is_valid("identifier", "Struct_1", None)
        )
        self.assertTrue(
            self.checker.check_if_variable_definition_is_valid("identifier", array_1, None)
        )
        self.assertTrue(
            self.checker.check_if_variable_definition_is_valid("identifier", array_2, None)
        )
        self.assertTrue(
            self.checker.check_if_variable_definition_is_valid("identifier", "Struct_2", None)
        )
        self.assertTrue(
            self.checker.check_if_variable_definition_is_valid("identifier", "number", None)
        )
        self.assertTrue(
            self.checker.check_if_variable_definition_is_valid("identifier", "string", None)
        )
        self.assertTrue(
            self.checker.check_if_variable_definition_is_valid("identifier", "boolean", None)
        )
        self.assertTrue(
            self.checker.check_if_variable_definition_is_valid("identifier", array_3, None)
        )

        self.assertFalse(
            self.checker.check_if_variable_definition_is_valid("identifier", "Not_a_struct", None)
        )
        self.assertFalse(
            self.checker.check_if_variable_definition_is_valid("identifier", array_4, None)
        )
        self.assertFalse(
            self.checker.check_if_variable_definition_is_valid(
                "identifier", "not_a_primitive_datatype", None
            )
        )
        self.assertFalse(
            self.checker.check_if_variable_definition_is_valid("identifier", array_5, None)
        )

    def test_check_if_task_in_taskcall_exists(self):
        self.checker.tasks = {"task_1": Task(), "task_2": Task()}
        self.assertTrue(self.checker.check_if_task_in_taskcall_exists("task_1", None))
        self.assertTrue(self.checker.check_if_task_in_taskcall_exists("task_2", None))
        self.assertFalse(self.checker.check_if_task_in_taskcall_exists("not_a_task", None))

    def test_check_array(self):
        array_definition = Array(type_of_elements="number")
        array_definition.length = 3

        instantiated_array = Array(values=[1, 2.0, 3])

        self.assertTrue(self.checker.check_array(instantiated_array, array_definition))

        # wrong type
        instantiated_array.values = [True, 2, 3]
        self.assertFalse(self.checker.check_array(instantiated_array, array_definition))

        instantiated_array.values = [1, "a string", 3]
        self.assertFalse(self.checker.check_array(instantiated_array, array_definition))

        instantiated_array.values = [True, 2, ""]
        self.assertFalse(self.checker.check_array(instantiated_array, array_definition))

        # wrong array length
        instantiated_array.length = 2
        instantiated_array.values = [1, 2]
        self.assertFalse(self.checker.check_array(instantiated_array, array_definition))

    def test_variable_type_exists(self):
        self.checker.structs = {"Struct_1": Struct(), "Struct_2": Struct()}

        self.assertTrue(self.checker.variable_type_exists("Struct_1"))
        self.assertTrue(self.checker.variable_type_exists("Struct_2"))
        self.assertTrue(self.checker.variable_type_exists("number"))
        self.assertTrue(self.checker.variable_type_exists("string"))
        self.assertTrue(self.checker.variable_type_exists("boolean"))

        self.assertFalse(self.checker.variable_type_exists("Not_a_struct"))
        self.assertFalse(self.checker.variable_type_exists("not_a_primitive_datatype"))

    def test_instantiated_array_length_correct(self):
        array_definition = Array()
        array_definition.length = 3

        instantiated_array = Array()
        instantiated_array.length = 3

        self.assertTrue(
            self.checker.instantiated_array_length_correct(instantiated_array, array_definition)
        )

        instantiated_array.length = 2
        self.assertFalse(
            self.checker.instantiated_array_length_correct(instantiated_array, array_definition)
        )

        array_definition.length = 1
        self.assertFalse(
            self.checker.instantiated_array_length_correct(instantiated_array, array_definition)
        )
