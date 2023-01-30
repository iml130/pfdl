# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains unit tests tests for the Scheduler class.

In the SemanticErrorChecker class, the model of the PFDL file is checked for static semantic errors.
If all methods in the visitor are correct, the model should not contain unexpected values. Thats
why there will be no checks for unexpected input args. Many methods are used to call a set of 
other tests methods. Here, mock objects are used to check if certain methods were called.
"""

# standard libraries
from typing import Dict
from pfdl_scheduler.model.condition import Condition
import unittest
from unittest.mock import Mock, patch
from pfdl_scheduler.model.parallel import Parallel

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

# global defines
from pfdl_scheduler.parser.pfdl_tree_visitor import IN_KEY, OUT_KEY


class DummyStart:
    def __init__(self):
        self.line = 0
        self.column = 0
        self.text = ""


class DummyContext:
    def __init__(self):
        self.start = DummyStart()


# ToDo: Check with mock objects if print error is called
class TestSemanticErrorChecker(unittest.TestCase):
    """Tests the methods of the SemanticErrorChecker.

    Most methods will require a created Process object
    """

    def setUp(self):
        self.process = Process()
        self.error_handler = ErrorHandler("", False)
        self.checker = SemanticErrorChecker(self.error_handler, self.process)
        self.dummy_context = DummyContext()

    def check_method(self, method_name: str, return_value: bool, calls: int, method, *args) -> bool:
        """Runs the given method with the help of a mock object which emulates a function.

        Args:
            method_name: The mock function which should be emulated.
            return_value: The return value of the mock function.
            calls: Specifies how many times the mock method should be called to pass the test.
            method: The method which should be tested.
            args: Variable amount of arguments for the method to be tested.
        """
        result = None
        with patch.object(self.checker, method_name, return_value=return_value) as mock:
            result = method(*args)
        self.assertEqual(mock.call_count, calls)
        return result

    def check_if_print_error_is_called(self, method, *args) -> None:
        """Runs the given method wiht the help of a mock object and checks if print error is called.

        Args:
            method: The method which should be tested.
            args: Variable amount of arguments for the method to be tested.
        """
        with patch.object(self.error_handler, "print_error") as mock:
            method(*args)
        mock.assert_called()

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

    def test_validate_process(self):
        self.checker.check_structs = Mock(return_value=True)
        self.checker.check_tasks = Mock(return_value=True)
        self.assertTrue(self.checker.validate_process())

        self.checker.check_structs = Mock(return_value=True)
        self.checker.check_tasks = Mock(return_value=False)
        self.assertFalse(self.checker.validate_process())

        self.checker.check_structs = Mock(return_value=False)
        self.checker.check_tasks = Mock(return_value=True)
        self.assertFalse(self.checker.validate_process())

        self.checker.check_structs = Mock(return_value=False)
        self.checker.check_tasks = Mock(return_value=False)
        self.assertFalse(self.checker.validate_process())

    def test_check_structs(self):
        self.checker.structs = {"struct_1": Mock(), "struct_2": Mock()}
        self.checker.check_for_unknown_datatypes_in_struct_definition = Mock(return_value=True)
        self.assertTrue(self.checker.check_structs())

        self.checker.structs = {"struct_1": Mock(), "struct_2": Mock()}
        self.checker.check_for_unknown_datatypes_in_struct_definition = Mock(return_value=False)
        self.assertFalse(self.checker.check_structs())

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

    def execute_check_tasks(self, p1: bool, p2: bool, p3: bool) -> bool:
        return_value = None

        with patch.object(self.checker, "check_statements", return_value=p1) as mock_1:
            with patch.object(
                self.checker, "check_task_input_parameters", return_value=p2
            ) as mock_2:
                with patch.object(
                    self.checker, "check_task_output_parameters", return_value=p3
                ) as mock_3:
                    return_value = self.checker.check_tasks()

        self.assertEqual(mock_1.call_count, 1)
        self.assertEqual(mock_2.call_count, 1)
        self.assertEqual(mock_3.call_count, 1)

        return return_value

    def test_check_tasks(self):
        self.checker.tasks = {"productionTask": Task(name="productionTask")}

        self.assertFalse(self.execute_check_tasks(False, False, False))
        self.assertFalse(self.execute_check_tasks(False, False, True))
        self.assertFalse(self.execute_check_tasks(False, True, False))
        self.assertFalse(self.execute_check_tasks(False, True, True))
        self.assertFalse(self.execute_check_tasks(True, False, False))
        self.assertFalse(self.execute_check_tasks(True, False, True))
        self.assertFalse(self.execute_check_tasks(True, True, False))
        self.assertTrue(self.execute_check_tasks(True, True, True))

        self.checker.tasks = {"noProductionTask": Task(name="noProductionTask")}
        self.assertFalse(self.execute_check_tasks(False, False, False))
        self.assertFalse(self.execute_check_tasks(True, True, True))

        self.check_if_print_error_is_called(self.execute_check_tasks, False, False, False)

    def test_check_statements(self):
        dummy_task = Task()
        dummy_task.statements = [Service()]

        args = ("check_statement", False, 1, self.checker.check_statements, dummy_task)
        self.assertFalse(self.check_method(*args))

        args = ("check_statement", True, 1, self.checker.check_statements, dummy_task)
        self.assertTrue(self.check_method(*args))

        dummy_task.statements = [Service(), Service()]

        args = ("check_statement", False, 2, self.checker.check_statements, dummy_task)
        self.assertFalse(self.check_method(*args))

    def test_check_statement(self):
        dummy_task = Task()

        args = ("check_service", False, 1, self.checker.check_statement, Service(), dummy_task)
        self.assertFalse(self.check_method(*args))

        args = ("check_task_call", False, 1, self.checker.check_statement, TaskCall(), dummy_task)
        self.assertFalse(self.check_method(*args))

        args = ("check_parallel", False, 1, self.checker.check_statement, Parallel(), dummy_task)
        self.assertFalse(self.check_method(*args))

        args = ("check_while_loop", False, 1, self.checker.check_statement, WhileLoop(), dummy_task)
        self.assertFalse(self.check_method(*args))

        args = (
            "check_counting_loop",
            False,
            1,
            self.checker.check_statement,
            CountingLoop(),
            dummy_task,
        )
        self.assertFalse(self.check_method(*args))

        args = (
            "check_conditional_statement",
            False,
            1,
            self.checker.check_statement,
            Condition(),
            dummy_task,
        )
        self.assertFalse(self.check_method(*args))

        args = ("check_service", True, 1, self.checker.check_statement, Service(), dummy_task)
        self.assertTrue(self.check_method(*args))

        args = ("check_task_call", True, 1, self.checker.check_statement, TaskCall(), dummy_task)
        self.assertTrue(self.check_method(*args))

        args = ("check_parallel", True, 1, self.checker.check_statement, Parallel(), dummy_task)
        self.assertTrue(self.check_method(*args))

        args = ("check_while_loop", True, 1, self.checker.check_statement, WhileLoop(), dummy_task)
        self.assertTrue(self.check_method(*args))

        args = (
            "check_counting_loop",
            True,
            1,
            self.checker.check_statement,
            CountingLoop(),
            dummy_task,
        )
        self.assertTrue(self.check_method(*args))

        args = (
            "check_conditional_statement",
            True,
            1,
            self.checker.check_statement,
            Condition(),
            dummy_task,
        )
        self.assertTrue(self.check_method(*args))

    def test_check_parallel(self):
        parallel = Parallel()
        dummy_task = Task()
        parallel.task_calls = []

        args = ("check_task_call", True, 0, self.checker.check_parallel, parallel, dummy_task)
        self.assertTrue(self.check_method(*args))

        parallel.task_calls = [TaskCall()]
        args = ("check_task_call", True, 1, self.checker.check_parallel, parallel, dummy_task)
        self.assertTrue(self.check_method(*args))

        parallel.task_calls = [TaskCall(), TaskCall(), TaskCall()]
        args = ("check_task_call", True, 3, self.checker.check_parallel, parallel, dummy_task)
        self.assertTrue(self.check_method(*args))

        parallel.task_calls = [TaskCall(), TaskCall(), TaskCall()]
        args = ("check_task_call", False, 3, self.checker.check_parallel, parallel, dummy_task)
        self.assertFalse(self.check_method(*args))

    def test_check_task_input_parameters(self):
        self.checker.structs = {"Struct_1": Struct(), "Struct_2": Struct()}
        dummy_task = Task()
        dummy_task.context_dict[IN_KEY] = DummyContext()

        dummy_task.input_parameters = {"input": "Struct_1"}
        args = (
            "check_if_variable_definition_is_valid",
            True,
            1,
            self.checker.check_task_input_parameters,
            dummy_task,
        )
        self.assertTrue(self.check_method(*args))

        dummy_task.input_parameters = {"input": "Struct_1", "input_2": "Struct_2"}
        self.assertTrue(self.checker.check_task_input_parameters(dummy_task))

        args = (
            "check_if_variable_definition_is_valid",
            True,
            2,
            self.checker.check_task_input_parameters,
            dummy_task,
        )
        self.assertTrue(self.check_method(*args))

        args = (
            "check_if_variable_definition_is_valid",
            False,
            2,
            self.checker.check_task_input_parameters,
            dummy_task,
        )
        self.assertFalse(self.check_method(*args))

    def test_check_task_output_parameters(self):
        dummy_task = Task()
        dummy_task.variables = ["var_1", "var_2", "var_3"]
        dummy_task.context_dict[OUT_KEY] = DummyContext()

        dummy_task.output_parameters = ["var_1", "var_2", "var_3"]
        self.assertTrue(self.checker.check_task_output_parameters(dummy_task))

        dummy_task.output_parameters = ["not_a_variable"]
        self.assertFalse(self.checker.check_task_output_parameters(dummy_task))

        dummy_task.output_parameters = ["var_1", "var_2", "not_a_variable"]
        self.assertFalse(self.checker.check_task_output_parameters(dummy_task))

        self.check_if_print_error_is_called(self.checker.check_task_output_parameters, dummy_task)

    def test_check_service(self):
        dummy_service = Service()
        dummy_task = Task()

        args = (
            "check_call_parameters",
            True,
            1,
            self.checker.check_service,
            dummy_service,
            dummy_task,
        )
        self.assertTrue(self.check_method(*args))

        args = (
            "check_call_parameters",
            False,
            1,
            self.checker.check_service,
            dummy_service,
            dummy_task,
        )
        self.assertFalse(self.check_method(*args))

    def test_check_task_call(self):
        dummy_task_call = TaskCall()
        dummy_task = Task()

        # we only need to check the other methods if the tascall exists, otherwise
        # further checks make no sense
        with patch.object(
            self.checker, "check_if_task_in_taskcall_exists", return_value=True
        ) as mock_1:
            with patch.object(self.checker, "check_call_parameters", return_value=True) as mock_2:
                with patch.object(
                    self.checker,
                    "check_if_task_call_matches_with_called_task",
                    return_value=True,
                ) as mock_3:
                    self.assertTrue(self.checker.check_task_call(dummy_task_call, dummy_task))

            mock_2.assert_called_once_with(dummy_task_call, dummy_task)
            mock_3.assert_called_once_with(dummy_task_call, dummy_task)

            with patch.object(self.checker, "check_call_parameters", return_value=True) as mock_2:
                with patch.object(
                    self.checker,
                    "check_if_task_call_matches_with_called_task",
                    return_value=False,
                ) as mock_3:
                    self.assertFalse(self.checker.check_task_call(dummy_task_call, dummy_task))

            mock_2.assert_called_once_with(dummy_task_call, dummy_task)
            mock_3.assert_called_once_with(dummy_task_call, dummy_task)

            with patch.object(self.checker, "check_call_parameters", return_value=False) as mock_2:
                with patch.object(
                    self.checker,
                    "check_if_task_call_matches_with_called_task",
                    return_value=True,
                ) as mock_3:
                    self.assertFalse(self.checker.check_task_call(dummy_task_call, dummy_task))

            mock_2.assert_called_once_with(dummy_task_call, dummy_task)
            mock_3.assert_not_called()

            with patch.object(self.checker, "check_call_parameters", return_value=False) as mock_2:
                with patch.object(
                    self.checker,
                    "check_if_task_call_matches_with_called_task",
                    return_value=False,
                ) as mock_3:
                    self.assertFalse(self.checker.check_task_call(dummy_task_call, dummy_task))

            mock_2.assert_called_once_with(dummy_task_call, dummy_task)
            mock_3.assert_not_called()

        mock_1.assert_called_with(dummy_task_call.name, dummy_task_call.context)

        with patch.object(
            self.checker, "check_if_task_in_taskcall_exists", return_value=False
        ) as mock_1:
            with patch.object(self.checker, "check_call_parameters", return_value=True) as mock_2:
                with patch.object(
                    self.checker,
                    "check_if_task_call_matches_with_called_task",
                    return_value=True,
                ) as mock_3:
                    self.assertFalse(self.checker.check_task_call(dummy_task_call, dummy_task))

        mock_1.assert_called_once_with(dummy_task_call.name, dummy_task_call.context)
        mock_2.assert_not_called()
        mock_3.assert_not_called()

    def test_check_if_task_call_matches_with_called_task(self):
        # (1) parameter length check
        dummy_task_context = Task("Task")
        dummy_called_task = Task("CalledTask")
        dummy_task_call = TaskCall("Task")
        self.checker.tasks = {"Task": dummy_called_task}

        args = (
            "check_if_task_call_parameter_length_match",
            True,
            1,
            self.checker.check_if_task_call_matches_with_called_task,
            dummy_task_call,
            dummy_task_context,
        )
        self.assertTrue(self.check_method(*args))

        args = (
            "check_if_task_call_parameter_length_match",
            False,
            1,
            self.checker.check_if_task_call_matches_with_called_task,
            dummy_task_call,
            dummy_task_context,
        )
        self.assertFalse(self.check_method(*args))

        # (2) input parameter check
        args = (dummy_task_call, dummy_task_context)

        dummy_task_call.input_parameters = ["input_1", "input_2"]
        dummy_called_task.input_parameters = {"param_1": "Struct_1", "param_2": "Struct_2"}

        with patch.object(
            self.checker, "check_if_input_parameter_matches", return_value=True
        ) as mock:
            self.assertTrue(self.checker.check_if_task_call_matches_with_called_task(*args))

        self.assertEqual(mock.call_count, 2)

        dummy_task_call.input_parameters = ["input_1"]
        dummy_called_task.input_parameters = {"param_1": "Struct_1"}
        with patch.object(
            self.checker, "check_if_input_parameter_matches", return_value=True
        ) as mock:
            self.assertTrue(self.checker.check_if_task_call_matches_with_called_task(*args))
            mock.assert_called_with(
                "input_1",
                "param_1",
                "Struct_1",
                TaskCall(),
                Task(),
                Task(),
            )
            self.assertIs(mock.call_args[0][3], dummy_task_call)
            self.assertIs(mock.call_args[0][4], dummy_called_task)
            self.assertIs(mock.call_args[0][5], dummy_task_context)

        with patch.object(
            self.checker, "check_if_input_parameter_matches", return_value=False
        ) as mock:
            self.assertFalse(self.checker.check_if_task_call_matches_with_called_task(*args))

        self.check_if_print_error_is_called(
            self.checker.check_if_task_call_matches_with_called_task, *args
        )

        # (3)output parameter check
        dummy_task_call.input_parameters = []
        dummy_called_task.input_parameters = {}
        dummy_called_task.variables = {"param_1": "Struct_1", "param_2": "Struct_2"}

        dummy_task_call.output_parameters = {"param_1": "Struct_1", "param_2": "Struct_2"}
        dummy_called_task.output_parameters = ["param_1", "param_2"]

        self.assertTrue(self.checker.check_if_task_call_matches_with_called_task(*args))

        dummy_called_task.variables = {"param_1": "Struct_1", "param_2": "Struct_3"}

        self.assertFalse(self.checker.check_if_task_call_matches_with_called_task(*args))

        self.check_if_print_error_is_called(
            self.checker.check_if_task_call_matches_with_called_task, *args
        )

    def test_check_if_input_parameter_matches(self):
        task_call = TaskCall("Task")
        task_context = Task()
        called_task = Task()

        # input parameter is str

        task_context.variables = {"test": "Struct_1"}
        args = ("test", "identifier", "Struct_1", task_call, called_task, task_context)
        self.assertTrue(self.checker.check_if_input_parameter_matches(*args))

        args = ("test", "identifier", "Struct_2", task_call, called_task, task_context)
        self.assertFalse(self.checker.check_if_input_parameter_matches(*args))
        self.check_if_print_error_is_called(self.checker.check_if_input_parameter_matches, *args)

        args = ("not_a_variable", "identifier", "Struct_1", task_call, called_task, task_context)
        self.assertFalse(self.checker.check_if_input_parameter_matches(*args))
        self.check_if_print_error_is_called(self.checker.check_if_input_parameter_matches, *args)

        # input parameter is List[str] without array

        # struct definitions
        dummy_struct_a = Struct("Struct_1")
        dummy_struct_b = Struct("Struct_2")
        dummy_struct_c = Struct("Struct_3")
        dummy_struct_a.attributes = {"b": "Struct_2"}
        dummy_struct_b.attributes = {"c": "Struct_3"}
        task_context.variables = {"a": "Struct_1"}
        self.checker.structs = {
            "Struct_1": dummy_struct_a,
            "Struct_2": dummy_struct_b,
            "Struct_3": dummy_struct_c,
        }

        args = (
            ["a", "b"],
            "identifier",
            "Struct_2",
            task_call,
            called_task,
            task_context,
        )
        self.assertTrue(self.checker.check_if_input_parameter_matches(*args))

        args = (
            ["a", "b", "c"],
            "identifier",
            "Struct_3",
            task_call,
            called_task,
            task_context,
        )
        self.assertTrue(self.checker.check_if_input_parameter_matches(*args))

        args = (
            ["a", "b", "c"],
            "identifier",
            "Struct_2",
            task_call,
            called_task,
            task_context,
        )
        self.assertFalse(self.checker.check_if_input_parameter_matches(*args))
        self.check_if_print_error_is_called(self.checker.check_if_input_parameter_matches, *args)

        # input parameter is List[str] with array
        dummy_struct_a = Struct("Struct_1")
        dummy_struct_b = Struct("Struct_2")
        dummy_struct_c = Struct("Struct_3")

        array = Array("Struct_2", [Struct(), Struct()])

        dummy_struct_a.attributes = {"b": array}
        dummy_struct_b.attributes = {"c": "Struct_3"}
        task_context.variables = {"a": "Struct_1"}
        self.checker.structs = {
            "Struct_1": dummy_struct_a,
            "Struct_2": dummy_struct_b,
            "Struct_3": dummy_struct_c,
        }

        args = (
            ["a", "b", "[]", "c"],
            "identifier",
            "Struct_3",
            task_call,
            called_task,
            task_context,
        )
        self.assertTrue(self.checker.check_if_input_parameter_matches(*args))

        args = (
            ["a", "b", "[]", "c"],
            "identifier",
            "Struct_2",
            task_call,
            called_task,
            task_context,
        )
        self.assertFalse(self.checker.check_if_input_parameter_matches(*args))
        self.check_if_print_error_is_called(self.checker.check_if_input_parameter_matches, *args)

        args = (
            ["a", "b", "[]"],
            "identifier",
            "Struct_2",
            task_call,
            called_task,
            task_context,
        )
        self.assertTrue(self.checker.check_if_input_parameter_matches(*args))

        args = (
            ["a", "b", "[]"],
            "identifier",
            "Struct_3",
            task_call,
            called_task,
            task_context,
        )
        self.assertFalse(self.checker.check_if_input_parameter_matches(*args))
        self.check_if_print_error_is_called(self.checker.check_if_input_parameter_matches, *args)

        # input parameter is Struct
        dummy_struct = Struct("Struct_1")
        args = (dummy_struct, "identifier", "Struct_1", task_call, called_task, task_context)
        self.assertTrue(self.checker.check_if_input_parameter_matches(*args))

        dummy_struct = Struct("Struct_2")
        args = (dummy_struct, "identifier", "Struct_1", task_call, called_task, task_context)
        self.assertFalse(self.checker.check_if_input_parameter_matches(*args))
        self.check_if_print_error_is_called(self.checker.check_if_input_parameter_matches, *args)

    def test_check_if_task_call_parameter_length_match(self):
        dummy_task = Task("task")
        task_call = TaskCall("task")
        self.checker.tasks = {"task": dummy_task}

        # input
        dummy_task.input_parameters = []
        task_call.input_parameters = {}
        self.assertTrue(self.checker.check_if_task_call_parameter_length_match(task_call))

        dummy_task.input_parameters = ["a"]
        task_call.input_parameters = {}
        self.assertFalse(self.checker.check_if_task_call_parameter_length_match(task_call))
        self.check_if_print_error_is_called(
            self.checker.check_if_task_call_parameter_length_match, task_call
        )

        dummy_task.input_parameters = []
        task_call.input_parameters = {"b": "type"}
        self.assertFalse(self.checker.check_if_task_call_parameter_length_match(task_call))
        self.check_if_print_error_is_called(
            self.checker.check_if_task_call_parameter_length_match, task_call
        )

        dummy_task.input_parameters = ["a"]
        task_call.input_parameters = {"b": "type"}
        self.assertTrue(self.checker.check_if_task_call_parameter_length_match(task_call))

        # output
        dummy_task.output_parameters = {}
        task_call.output_parameters = []
        self.assertTrue(self.checker.check_if_task_call_parameter_length_match(task_call))

        dummy_task.output_parameters = {"a": "type"}
        task_call.output_parameters = []
        self.assertFalse(self.checker.check_if_task_call_parameter_length_match(task_call))
        self.check_if_print_error_is_called(
            self.checker.check_if_task_call_parameter_length_match, task_call
        )

        dummy_task.output_parameters = {}
        task_call.output_parameters = ["b"]
        self.assertFalse(self.checker.check_if_task_call_parameter_length_match(task_call))
        self.check_if_print_error_is_called(
            self.checker.check_if_task_call_parameter_length_match, task_call
        )

        dummy_task.output_parameters = {"a": "type"}
        task_call.output_parameters = ["b"]
        self.assertTrue(self.checker.check_if_task_call_parameter_length_match(task_call))

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
        task_call.input_parameters = []
        task_call.output_parameters = {}

        with patch.object(self.checker, "check_call_input_parameters") as input:
            with patch.object(self.checker, "check_call_output_parameters") as output:
                self.checker.check_call_parameters(task_call, task)
        input.assert_not_called()
        output.assert_not_called()

    def test_check_call_input_parameters(self):
        task_context = Task()
        service = Service()
        task_call = TaskCall()
        # no input parameters
        self.assertTrue(self.checker.check_call_input_parameters(service, task_context))
        self.assertTrue(self.checker.check_call_input_parameters(task_call, task_context))

        # input parameter is struct
        service.input_parameters = [Struct()]

        args = (
            "check_instantiated_struct_attributes",
            True,
            1,
            self.checker.check_call_input_parameters,
            service,
            task_context,
        )
        self.assertTrue(self.check_method(*args))

        args = (
            "check_instantiated_struct_attributes",
            False,
            1,
            self.checker.check_call_input_parameters,
            service,
            task_context,
        )
        self.assertFalse(self.check_method(*args))

        task_call.input_parameters = [Struct()]
        args = (
            "check_instantiated_struct_attributes",
            True,
            1,
            self.checker.check_call_input_parameters,
            task_call,
            task_context,
        )
        self.assertTrue(self.check_method(*args))

        args = (
            "check_instantiated_struct_attributes",
            False,
            1,
            self.checker.check_call_input_parameters,
            task_call,
            task_context,
        )
        self.assertFalse(self.check_method(*args))

        service.input_parameters = [Struct(), Struct(), Struct()]
        args = (
            "check_instantiated_struct_attributes",
            True,
            3,
            self.checker.check_call_input_parameters,
            service,
            task_context,
        )
        self.assertTrue(self.check_method(*args))

        # input parameter is list
        service.input_parameters = [[]]
        service.context_dict[IN_KEY] = None
        args = (
            "check_attribute_access",
            True,
            1,
            self.checker.check_call_input_parameters,
            service,
            task_context,
        )
        self.assertTrue(self.check_method(*args))

        args = (
            "check_attribute_access",
            False,
            1,
            self.checker.check_call_input_parameters,
            service,
            task_context,
        )
        self.assertFalse(self.check_method(*args))

        task_call.input_parameters = [[]]
        task_call.context_dict[IN_KEY] = None
        args = (
            "check_attribute_access",
            True,
            1,
            self.checker.check_call_input_parameters,
            task_call,
            task_context,
        )
        self.assertTrue(self.check_method(*args))

        args = (
            "check_attribute_access",
            False,
            1,
            self.checker.check_call_input_parameters,
            task_call,
            task_context,
        )
        self.assertFalse(self.check_method(*args))

        service.input_parameters = [[], [], []]
        args = (
            "check_attribute_access",
            True,
            3,
            self.checker.check_call_input_parameters,
            service,
            task_context,
        )
        self.assertTrue(self.check_method(*args))

        # input parameter is string
        service.input_parameters = ["test"]
        self.assertFalse(self.checker.check_call_input_parameters(service, task_context))
        self.check_if_print_error_is_called(
            self.checker.check_call_input_parameters, service, task_context
        )

        task_call.input_parameters = ["test"]
        self.assertFalse(self.checker.check_call_input_parameters(task_call, task_context))
        self.check_if_print_error_is_called(
            self.checker.check_call_input_parameters, service, task_context
        )

        task_context.variables = {"test": Struct()}
        self.assertTrue(self.checker.check_call_input_parameters(service, task_context))
        self.assertTrue(self.checker.check_call_input_parameters(task_call, task_context))

        # mix of input parameters
        service.input_parameters = ["test", [], Struct()]
        with patch.object(
            self.checker, "check_instantiated_struct_attributes", return_value=True
        ) as mock_1:
            with patch.object(self.checker, "check_attribute_access", return_value=True) as mock_2:
                self.assertTrue(self.checker.check_call_input_parameters(service, task_context))

        mock_1.assert_called_once()
        mock_2.assert_called_once()

    def test_check_attribute_access(self):
        dummy_context = DummyContext()
        dummy_task = Task()

        dummy_struct_a = Struct("Struct_1")
        dummy_struct_b = Struct("Struct_2")
        dummy_struct_c = Struct("Struct_3")

        self.checker.structs = {
            "Struct_1": dummy_struct_a,
            "Struct_2": dummy_struct_b,
            "Struct_3": dummy_struct_c,
        }

        # unknown variable
        dummy_task.variables = {""}
        attribute_access = ["a", "b"]
        self.assertFalse(
            self.checker.check_attribute_access(attribute_access, dummy_context, dummy_task)
        )
        self.check_if_print_error_is_called(
            self.checker.check_attribute_access, attribute_access, dummy_context, dummy_task
        )

        dummy_task.variables = {"a": "Struct_1"}
        dummy_struct_a.attributes = {"b": "Struct_2"}
        self.assertTrue(
            self.checker.check_attribute_access(attribute_access, dummy_context, dummy_task)
        )

        dummy_struct_b.attributes = {"c": "Struct_3"}

        attribute_access = ["a", "b", "c"]
        self.assertTrue(
            self.checker.check_attribute_access(attribute_access, dummy_context, dummy_task)
        )

        attribute_access = ["a", "b", "d"]
        self.assertFalse(
            self.checker.check_attribute_access(attribute_access, dummy_context, dummy_task)
        )
        self.check_if_print_error_is_called(
            self.checker.check_attribute_access, attribute_access, dummy_context, dummy_task
        )

        attribute_access = ["a", "e", "c"]
        self.assertFalse(
            self.checker.check_attribute_access(attribute_access, dummy_context, dummy_task)
        )
        self.check_if_print_error_is_called(
            self.checker.check_attribute_access, attribute_access, dummy_context, dummy_task
        )

        dummy_struct_a.attributes = {"b": "Unknown Struct"}
        attribute_access = ["a", "b", "c"]
        self.assertFalse(
            self.checker.check_attribute_access(attribute_access, dummy_context, dummy_task)
        )
        self.check_if_print_error_is_called(
            self.checker.check_attribute_access, attribute_access, dummy_context, dummy_task
        )

        # with array
        dummy_struct_a.attributes = {"b": Array("Struct_2")}

        attribute_access = ["a", "b", "[]"]
        self.assertTrue(
            self.checker.check_attribute_access(attribute_access, dummy_context, dummy_task)
        )

        attribute_access = ["a", "b", "[]", "c"]
        self.assertTrue(
            self.checker.check_attribute_access(attribute_access, dummy_context, dummy_task)
        )
        attribute_access = ["a", "b", "[]", "d"]
        self.assertFalse(
            self.checker.check_attribute_access(attribute_access, dummy_context, dummy_task)
        )
        self.check_if_print_error_is_called(
            self.checker.check_attribute_access, attribute_access, dummy_context, dummy_task
        )

    def test_check_call_output_parameters(self):
        # True
        service_call = Service()
        service_call.output_parameters = {"1": ""}

        args = (
            "check_if_variable_definition_is_valid",
            True,
            1,
            self.checker.check_call_output_parameters,
            service_call,
        )
        self.assertTrue(self.check_method(*args))

        service_call.output_parameters = {"1": "", "2": "", "3": ""}
        args = (
            "check_if_variable_definition_is_valid",
            True,
            3,
            self.checker.check_call_output_parameters,
            service_call,
        )
        self.assertTrue(self.check_method(*args))

        task_call = TaskCall()
        task_call.output_parameters = {"1": ""}
        args = (
            "check_if_variable_definition_is_valid",
            True,
            1,
            self.checker.check_call_output_parameters,
            task_call,
        )
        self.assertTrue(self.check_method(*args))

        task_call = TaskCall()
        task_call.output_parameters = {"1": "", "2": "", "3": ""}
        args = (
            "check_if_variable_definition_is_valid",
            True,
            3,
            self.checker.check_call_output_parameters,
            task_call,
        )
        self.assertTrue(self.check_method(*args))

        # False
        service_call.output_parameters = {"1": ""}
        args = (
            "check_if_variable_definition_is_valid",
            False,
            1,
            self.checker.check_call_output_parameters,
            service_call,
        )
        self.assertFalse(self.check_method(*args))

        service_call.output_parameters = {"1": "", "2": "", "3": ""}
        args = (
            "check_if_variable_definition_is_valid",
            False,
            3,
            self.checker.check_call_output_parameters,
            service_call,
        )
        self.assertFalse(self.check_method(*args))

        task_call = TaskCall()
        task_call.output_parameters = {"1": ""}
        args = (
            "check_if_variable_definition_is_valid",
            False,
            1,
            self.checker.check_call_output_parameters,
            task_call,
        )
        self.assertFalse(self.check_method(*args))

        task_call = TaskCall()
        task_call.output_parameters = {"1": "", "2": "", "3": ""}
        args = (
            "check_if_variable_definition_is_valid",
            False,
            3,
            self.checker.check_call_output_parameters,
            task_call,
        )
        self.assertFalse(self.check_method(*args))

    def test_check_instantiated_struct_attributes(self):
        instantiated_struct = Struct("Struct_1")
        self.checker.structs = {"Struct_1": Struct()}

        with patch.object(self.checker, "check_if_struct_exists", return_value=True) as mock_1:
            self.assertTrue(self.checker.check_instantiated_struct_attributes(instantiated_struct))

            with patch.object(
                self.checker, "check_for_missing_attribute_in_struct", return_value=True
            ) as mock_2:
                self.assertTrue(
                    self.checker.check_instantiated_struct_attributes(instantiated_struct)
                )

                instantiated_struct.attributes = {"attr_1": 1}
                self.checker.structs = {"Struct_1": Struct("", {"attr_1": "number"})}

                with patch.object(
                    self.checker, "check_for_unknown_attribute_in_struct", return_value=True
                ) as mock_3:
                    self.assertTrue(
                        self.checker.check_instantiated_struct_attributes(instantiated_struct)
                    )
                mock_3.assert_called_once()
                with patch.object(
                    self.checker, "check_for_wrong_attribute_type_in_struct", return_value=True
                ) as mock_3:
                    self.assertTrue(
                        self.checker.check_instantiated_struct_attributes(instantiated_struct)
                    )
                mock_3.assert_called_once()

                instantiated_struct.attributes = {"attr_1": 1, "attr_2": 2, "attr_3": 3}
                self.checker.structs = {
                    "Struct_1": Struct(
                        "", {"attr_1": "number", "attr_2": "number", "attr_3": "number"}
                    )
                }
                with patch.object(
                    self.checker, "check_for_unknown_attribute_in_struct", return_value=False
                ) as mock_3:
                    self.assertFalse(
                        self.checker.check_instantiated_struct_attributes(instantiated_struct)
                    )
                self.assertEqual(mock_3.call_count, 3)
                with patch.object(
                    self.checker, "check_for_wrong_attribute_type_in_struct", return_value=False
                ) as mock_3:
                    self.assertFalse(
                        self.checker.check_instantiated_struct_attributes(instantiated_struct)
                    )
                self.assertEqual(mock_3.call_count, 3)

            mock_2.assert_called()

            with patch.object(
                self.checker, "check_for_missing_attribute_in_struct", return_value=False
            ) as mock_2:
                self.assertFalse(
                    self.checker.check_instantiated_struct_attributes(instantiated_struct)
                )
            mock_2.assert_called_once()

        args = (
            "check_if_struct_exists",
            False,
            1,
            self.checker.check_instantiated_struct_attributes,
            instantiated_struct,
        )
        self.assertFalse(self.check_method(*args))

    def test_check_if_struct_exists(self):
        self.checker.structs = {"Struct_1": Struct(), "Struct_2": Struct()}
        self.assertTrue(self.checker.check_if_struct_exists(Struct("Struct_1")))
        self.assertTrue(self.checker.check_if_struct_exists(Struct("Struct_2")))
        self.assertFalse(self.checker.check_if_struct_exists(Struct("Not_a_struct")))
        self.check_if_print_error_is_called(
            self.checker.check_if_struct_exists, Struct("Not_a_struct")
        )

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
        self.check_if_print_error_is_called(
            self.checker.check_for_unknown_attribute_in_struct,
            instantiated_struct,
            "unknown_identifier",
            struct_definition,
        )

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
        self.check_if_print_error_is_called(
            self.checker.check_for_wrong_attribute_type_in_struct,
            instantiated_struct,
            "identifier_1",
            struct_definition,
        )

        instantiated_struct.attributes = {"identifier_1": Array()}
        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "identifier_1", struct_definition
        )
        self.assertFalse(check_result)
        self.check_if_print_error_is_called(
            self.checker.check_for_wrong_attribute_type_in_struct,
            instantiated_struct,
            "identifier_1",
            struct_definition,
        )

        instantiated_struct.attributes = {"identifier_1": True}
        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "identifier_1", struct_definition
        )
        self.assertFalse(check_result)
        self.check_if_print_error_is_called(
            self.checker.check_for_wrong_attribute_type_in_struct,
            instantiated_struct,
            "identifier_1",
            struct_definition,
        )

        instantiated_struct.attributes = {"identifier_1": Struct()}
        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "identifier_1", struct_definition
        )
        self.assertFalse(check_result)
        self.check_if_print_error_is_called(
            self.checker.check_for_wrong_attribute_type_in_struct,
            instantiated_struct,
            "identifier_1",
            struct_definition,
        )

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
        self.check_if_print_error_is_called(
            self.checker.check_for_wrong_attribute_type_in_struct,
            instantiated_struct,
            "identifier_1",
            struct_definition,
        )

        instantiated_struct.attributes = {"identifier_1": Array()}
        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "identifier_1", struct_definition
        )
        self.assertFalse(check_result)
        self.check_if_print_error_is_called(
            self.checker.check_for_wrong_attribute_type_in_struct,
            instantiated_struct,
            "identifier_1",
            struct_definition,
        )

        instantiated_struct.attributes = {"identifier_1": True}
        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "identifier_1", struct_definition
        )
        self.assertFalse(check_result)
        self.check_if_print_error_is_called(
            self.checker.check_for_wrong_attribute_type_in_struct,
            instantiated_struct,
            "identifier_1",
            struct_definition,
        )

        instantiated_struct.attributes = {"identifier_1": Struct()}
        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "identifier_1", struct_definition
        )
        self.assertFalse(check_result)
        self.check_if_print_error_is_called(
            self.checker.check_for_wrong_attribute_type_in_struct,
            instantiated_struct,
            "identifier_1",
            struct_definition,
        )

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
        self.check_if_print_error_is_called(
            self.checker.check_for_wrong_attribute_type_in_struct,
            instantiated_struct,
            "identifier_1",
            struct_definition,
        )

        instantiated_struct.attributes = {"identifier_1": Array()}
        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "identifier_1", struct_definition
        )
        self.assertFalse(check_result)
        self.check_if_print_error_is_called(
            self.checker.check_for_wrong_attribute_type_in_struct,
            instantiated_struct,
            "identifier_1",
            struct_definition,
        )

        instantiated_struct.attributes = {"identifier_1": 5}
        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "identifier_1", struct_definition
        )
        self.assertFalse(check_result)
        self.check_if_print_error_is_called(
            self.checker.check_for_wrong_attribute_type_in_struct,
            instantiated_struct,
            "identifier_1",
            struct_definition,
        )

        instantiated_struct.attributes = {"identifier_1": Struct()}
        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "identifier_1", struct_definition
        )
        self.assertFalse(check_result)
        self.check_if_print_error_is_called(
            self.checker.check_for_wrong_attribute_type_in_struct,
            instantiated_struct,
            "identifier_1",
            struct_definition,
        )

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
        self.check_if_print_error_is_called(
            self.checker.check_for_wrong_attribute_type_in_struct,
            instantiated_struct,
            "identifier_1",
            struct_definition,
        )

        instantiated_struct.attributes = {"identifier_1": 5}
        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "identifier_1", struct_definition
        )
        self.assertFalse(check_result)
        self.check_if_print_error_is_called(
            self.checker.check_for_wrong_attribute_type_in_struct,
            instantiated_struct,
            "identifier_1",
            struct_definition,
        )

        instantiated_struct.attributes = {"identifier_1": True}
        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "identifier_1", struct_definition
        )
        self.assertFalse(check_result)
        self.check_if_print_error_is_called(
            self.checker.check_for_wrong_attribute_type_in_struct,
            instantiated_struct,
            "identifier_1",
            struct_definition,
        )

        instantiated_struct.attributes = {"identifier_1": Struct()}
        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "identifier_1", struct_definition
        )
        self.assertFalse(check_result)
        self.check_if_print_error_is_called(
            self.checker.check_for_wrong_attribute_type_in_struct,
            instantiated_struct,
            "identifier_1",
            struct_definition,
        )

        # type is struct
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

        instantiated_struct.attributes = {"nested_struct": "not_a_struct_name"}

        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "nested_struct", struct_definition
        )
        self.assertFalse(check_result)
        self.check_if_print_error_is_called(
            self.checker.check_for_wrong_attribute_type_in_struct,
            instantiated_struct,
            "nested_struct",
            struct_definition,
        )

        instantiated_struct.attributes = {"nested_struct": Array()}
        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "nested_struct", struct_definition
        )
        self.assertFalse(check_result)
        self.check_if_print_error_is_called(
            self.checker.check_for_wrong_attribute_type_in_struct,
            instantiated_struct,
            "nested_struct",
            struct_definition,
        )

        instantiated_struct.attributes = {"nested_struct": True}
        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "nested_struct", struct_definition
        )
        self.assertFalse(check_result)
        self.check_if_print_error_is_called(
            self.checker.check_for_wrong_attribute_type_in_struct,
            instantiated_struct,
            "nested_struct",
            struct_definition,
        )

        instantiated_struct.attributes = {"nested_struct": 5}
        check_result = self.checker.check_for_wrong_attribute_type_in_struct(
            instantiated_struct, "nested_struct", struct_definition
        )
        self.assertFalse(check_result)
        self.check_if_print_error_is_called(
            self.checker.check_for_wrong_attribute_type_in_struct,
            instantiated_struct,
            "nested_struct",
            struct_definition,
        )

        instantiated_struct.attributes = {"nested_struct": nested_struct}
        args = (
            "check_for_wrong_attribute_type_in_struct",
            True,
            1,
            self.checker.check_for_wrong_attribute_type_in_struct,
            instantiated_struct,
            "nested_struct",
            struct_definition,
        )
        self.assertTrue(self.check_method(*args))

        args = (
            "check_for_wrong_attribute_type_in_struct",
            False,
            1,
            self.checker.check_for_wrong_attribute_type_in_struct,
            instantiated_struct,
            "nested_struct",
            struct_definition,
        )
        self.assertFalse(self.check_method(*args))

    def test_check_for_missing_attribute_in_struct(self):
        struct_definition = Struct()
        struct_definition.name = "Test"
        instantiated_struct = Struct()
        instantiated_struct.context_dict["identifier_1"] = DummyContext()

        struct_definition.attributes = {"identifier_1": "string"}
        instantiated_struct.attributes = {"identifier_1": '"a string"'}

        self.assertTrue(
            self.checker.check_for_missing_attribute_in_struct(
                instantiated_struct, struct_definition
            )
        )

        struct_definition.attributes = {"identifier_1": "string"}
        instantiated_struct.attributes = {"identifier_2": '"a string"'}

        self.assertFalse(
            self.checker.check_for_missing_attribute_in_struct(
                instantiated_struct, struct_definition
            )
        )

    def test_check_while_loop(self):
        expression = {"True"}
        task = Task()

        while_loop = WhileLoop(expression=expression)
        while_loop.statements = [Service(), Service(), TaskCall()]

        with patch.object(self.checker, "check_statement") as mock_1:
            with patch.object(self.checker, "check_expression") as mock_2:
                self.checker.check_while_loop(while_loop, task)
        self.assertEqual(mock_1.call_count, 3)
        mock_2.assert_called_with(expression, None, task)

        while_loop.statements = [Service(), Service(), TaskCall(), TaskCall(), TaskCall()]
        args = ("check_statement", False, 5, self.checker.check_while_loop, while_loop, task)
        self.assertFalse(self.check_method(*args))

        while_loop.statements = [Service()]
        args = ("check_statement", True, 1, self.checker.check_while_loop, while_loop, task)
        self.assertTrue(self.check_method(*args))

        args = ("check_expression", True, 1, self.checker.check_while_loop, while_loop, task)
        self.assertTrue(self.check_method(*args))

        args = ("check_expression", False, 1, self.checker.check_while_loop, while_loop, task)
        self.assertFalse(self.check_method(*args))

    def test_check_counting_loop(self):
        task = Task()

        counting_loop = CountingLoop()

        counting_loop.statements = [Service()]
        args = ("check_statement", True, 1, self.checker.check_counting_loop, counting_loop, task)
        self.assertTrue(self.check_method(*args))

        counting_loop.statements = [
            Service(),
            Service(),
            TaskCall(),
        ]

        args = ("check_statement", True, 3, self.checker.check_counting_loop, counting_loop, task)
        self.assertTrue(self.check_method(*args))

        args = ("check_statement", False, 3, self.checker.check_counting_loop, counting_loop, task)
        self.assertFalse(self.check_method(*args))

    def test_check_conditional_statement(self):
        expression = {"True"}
        task = Task()

        condition = Condition(expression=expression)

        args = (
            "check_statement",
            True,
            1,
            self.checker.check_conditional_statement,
            condition,
            task,
        )

        condition.passed_stmts = [Service()]
        condition.failed_stmts = []

        self.assertTrue(self.check_method(*args))

        condition.passed_stmts = []
        condition.failed_stmts = [Service()]

        self.assertTrue(self.check_method(*args))

        condition.passed_stmts = [Service(), Service()]
        condition.failed_stmts = [TaskCall()]

        args = (
            "check_statement",
            True,
            3,
            self.checker.check_conditional_statement,
            condition,
            task,
        )

        self.assertTrue(self.check_method(*args))

        args = (
            "check_statement",
            False,
            3,
            self.checker.check_conditional_statement,
            condition,
            task,
        )
        self.assertFalse(self.check_method(*args))

        with patch.object(self.checker, "check_statement", return_value=True) as mock:
            args = (
                "check_expression",
                True,
                1,
                self.checker.check_conditional_statement,
                condition,
                task,
            )

            self.assertTrue(self.check_method(*args))

            args = (
                "check_expression",
                False,
                1,
                self.checker.check_conditional_statement,
                condition,
                task,
            )

            self.assertFalse(self.check_method(*args))

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
        self.check_if_print_error_is_called(
            self.checker.check_expression, {"unop": "!", "value": variable_list_2}, None, task
        )

        expression = {
            "left": variable_list_2,
            "binOp": "Or",
            "right": {"left": 5, "binOp": "<", "right": variable_list},
        }
        self.assertFalse(
            self.checker.check_expression({"unop": "!", "value": expression}, None, task)
        )
        self.check_if_print_error_is_called(
            self.checker.check_expression, {"unop": "!", "value": expression}, None, task
        )

        expression = {
            "left": variable_list_3,
            "binOp": "Or",
            "right": {"left": "True", "binOp": "<", "right": variable_list},
        }
        self.assertFalse(
            self.checker.check_expression({"unop": "!", "value": expression}, None, task)
        )
        self.check_if_print_error_is_called(
            self.checker.check_expression, {"unop": "!", "value": expression}, None, task
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
        self.check_if_print_error_is_called(
            self.checker.check_expression, {"unop": "!", "value": expression}, None, task
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
        self.check_if_print_error_is_called(
            self.checker.check_expression,
            {"left": 5, "binOp": "<", "right": "a_string"},
            None,
            task,
        )

        self.assertFalse(
            self.checker.check_expression(
                {"left": variable_list_2, "binOp": "<", "right": 1}, None, task
            )
        )
        self.check_if_print_error_is_called(
            self.checker.check_expression,
            {"left": variable_list_2, "binOp": "<", "right": 1},
            None,
            task,
        )

        self.assertFalse(
            self.checker.check_expression(
                {"left": variable_list_3, "binOp": "<", "right": 1}, None, task
            )
        )
        self.check_if_print_error_is_called(
            self.checker.check_expression,
            {"left": variable_list_3, "binOp": "<", "right": 1},
            None,
            task,
        )

        expression = {
            "left": variable_list_2,
            "binOp": "Or",
            "right": {"left": 5, "binOp": "<", "right": variable_list},
        }
        self.assertFalse(self.checker.check_expression(expression, None, task))
        self.check_if_print_error_is_called(
            self.checker.check_expression,
            expression,
            None,
            task,
        )

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
        self.check_if_print_error_is_called(
            self.checker.check_expression,
            expression,
            None,
            task,
        )

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

        # invalid attribute access
        args = (
            "check_attribute_access",
            False,
            1,
            self.checker.check_single_expression,
            [],
            None,
            None,
        )
        self.assertFalse(self.check_method(*args))

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
            self.checker.check_binary_operation({"left": 5, "binOp": "+", "right": 10}, None, task)
        )
        self.assertTrue(
            self.checker.check_binary_operation({"left": 5, "binOp": "-", "right": 10}, None, task)
        )
        self.assertTrue(
            self.checker.check_binary_operation({"left": 5, "binOp": "/", "right": 10}, None, task)
        )
        self.assertTrue(
            self.checker.check_binary_operation({"left": 5, "binOp": "*", "right": 10}, None, task)
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
                {"left": 5, "binOp": "+", "right": "a_string"}, None, task
            )
        )
        self.assertFalse(
            self.checker.check_binary_operation(
                {"left": "a_string", "binOp": "+", "right": "5"}, None, task
            )
        )
        self.assertFalse(
            self.checker.check_binary_operation(
                {"left": 5, "binOp": "-", "right": "a_string"}, None, task
            )
        )
        self.assertFalse(
            self.checker.check_binary_operation(
                {"left": 5, "binOp": "/", "right": "a_string"}, None, task
            )
        )
        self.assertFalse(
            self.checker.check_binary_operation(
                {"left": 5, "binOp": "*", "right": "a_string"}, None, task
            )
        )
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

        self.assertTrue(
            self.checker.expression_is_number({"left": 5, "binOp": "<", "right": 10}, task)
        )
        self.assertFalse(
            self.checker.expression_is_number(
                {"left": 5, "binOp": "<", "right": "not a number"}, task
            )
        )

        expression = {
            "left": "(",
            "binOp": {"left": 5, "binOp": "<", "right": 10},
            "right": ")",
        }
        self.assertTrue(self.checker.expression_is_number(expression, task))

        expression = {
            "left": "(",
            "binOp": {"left": 5, "binOp": "<", "right": "not a number"},
            "right": ")",
        }
        self.assertFalse(self.checker.expression_is_number(expression, task))

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
        self.check_if_print_error_is_called(
            self.checker.check_if_variable_definition_is_valid,
            "identifier",
            "Not_a_struct",
            None,
        )

        self.assertFalse(
            self.checker.check_if_variable_definition_is_valid("identifier", array_4, None)
        )
        self.check_if_print_error_is_called(
            self.checker.check_if_variable_definition_is_valid,
            "identifier",
            array_4,
            None,
        )

        self.assertFalse(
            self.checker.check_if_variable_definition_is_valid(
                "identifier", "not_a_primitive_datatype", None
            )
        )
        self.check_if_print_error_is_called(
            self.checker.check_if_variable_definition_is_valid,
            "identifier",
            "not_a_primitive_datatype",
            None,
        )

        self.assertFalse(
            self.checker.check_if_variable_definition_is_valid("identifier", array_5, None)
        )
        self.check_if_print_error_is_called(
            self.checker.check_if_variable_definition_is_valid,
            "identifier",
            array_5,
            None,
        )

    def test_check_if_task_in_taskcall_exists(self):
        self.checker.tasks = {"task_1": Task(), "task_2": Task()}
        self.assertTrue(self.checker.check_if_task_in_taskcall_exists("task_1", None))
        self.assertTrue(self.checker.check_if_task_in_taskcall_exists("task_2", None))
        self.assertFalse(self.checker.check_if_task_in_taskcall_exists("not_a_task", None))
        self.check_if_print_error_is_called(
            self.checker.check_if_task_in_taskcall_exists, "not_a_task", None
        )

    def test_check_array(self):
        array_definition = Array(type_of_elements="number")
        array_definition.length = 3

        instantiated_array = Array(values=[1, 2.0, 3])

        self.assertTrue(self.checker.check_array(instantiated_array, array_definition))

        # wrong type
        instantiated_array.values = [True, 2, 3]
        self.assertFalse(self.checker.check_array(instantiated_array, array_definition))
        self.check_if_print_error_is_called(
            self.checker.check_array, instantiated_array, array_definition
        )

        instantiated_array.values = [1, "a string", 3]
        self.assertFalse(self.checker.check_array(instantiated_array, array_definition))
        self.check_if_print_error_is_called(
            self.checker.check_array, instantiated_array, array_definition
        )

        instantiated_array.values = [True, 2, ""]
        self.assertFalse(self.checker.check_array(instantiated_array, array_definition))
        self.check_if_print_error_is_called(
            self.checker.check_array, instantiated_array, array_definition
        )

        # struct in array
        array_definition = Array(type_of_elements="Struct_1")
        array_definition.length = 1

        instantiated_array.values = [Struct("Struct_1")]
        instantiated_array.length = 1
        args = (
            "check_instantiated_struct_attributes",
            True,
            1,
            self.checker.check_array,
            instantiated_array,
            array_definition,
        )
        self.assertTrue(self.check_method(*args))

        args = (
            "check_instantiated_struct_attributes",
            False,
            1,
            self.checker.check_array,
            instantiated_array,
            array_definition,
        )
        self.assertFalse(self.check_method(*args))

        instantiated_array.values = [Struct("Struct_2")]
        args = (
            "check_instantiated_struct_attributes",
            True,
            1,
            self.checker.check_array,
            instantiated_array,
            array_definition,
        )
        self.assertFalse(self.check_method(*args))

        # wrong array length
        array_definition.length = 1
        instantiated_array.length = 2
        instantiated_array.values = [1, 2]
        self.assertFalse(self.checker.check_array(instantiated_array, array_definition))
        self.check_if_print_error_is_called(
            self.checker.check_array, instantiated_array, array_definition
        )

        # struct type not set yet
        array_definition = Array(type_of_elements="Struct_1")
        array_definition.length = 1

        struct_without_type = Struct()
        instantiated_array.values = [struct_without_type]
        instantiated_array.length = 1

        args = (
            "check_instantiated_struct_attributes",
            True,
            1,
            self.checker.check_array,
            instantiated_array,
            array_definition,
        )
        self.assertTrue(self.check_method(*args))
        self.assertEqual(struct_without_type.name, "Struct_1")

        args = (
            "check_instantiated_struct_attributes",
            False,
            1,
            self.checker.check_array,
            instantiated_array,
            array_definition,
        )
        self.assertFalse(self.check_method(*args))
        self.assertEqual(struct_without_type.name, "Struct_1")

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
