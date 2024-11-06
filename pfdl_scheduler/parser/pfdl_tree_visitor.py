# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains PFDLTreeVisitor class."""

# standard libraries
from typing import Dict, List, OrderedDict, Tuple, Union
from pfdl_scheduler.model.instance import Instance
from pfdl_scheduler.pfdl_base_classes import PFDLBaseClasses
from pfdl_scheduler.utils import helpers
from pfdl_scheduler.model.parallel import Parallel

# 3rd party
from antlr4.tree.Tree import TerminalNodeImpl

# local sources
from pfdl_scheduler.validation.error_handler import ErrorHandler

from pfdl_scheduler.parser.PFDLParserVisitor import PFDLParserVisitor
from pfdl_scheduler.parser.PFDLParser import PFDLParser

from pfdl_scheduler.model.process import Process
from pfdl_scheduler.model.struct import Struct
from pfdl_scheduler.model.task import Task
from pfdl_scheduler.model.service import Service
from pfdl_scheduler.model.task_call import TaskCall
from pfdl_scheduler.model.condition import Condition
from pfdl_scheduler.model.counting_loop import CountingLoop
from pfdl_scheduler.model.while_loop import WhileLoop
from pfdl_scheduler.model.array import Array


PRIMITIVE_DATATYPES: List[str] = ["number", "string", "boolean"]
IN_KEY: str = "in"
OUT_KEY: str = "out"
START_TASK: str = "productionTask"


class PFDLTreeVisitor(PFDLParserVisitor):
    """Traverses the given parse tree and store program information in a Process object.

    This class overrides the generated visitor methods from the ANTLR generated
    PFDLParserVisitor. A Process object is created and gets filled while traversing
    the syntax tree.

    Attributes:
        error_handler: ErrorHandler instance for printing errors while visiting.
        current_task: Reference to the currently visited Task. Every visitor method can access it.
        pfdl_base_classes: `PFDLBaseClasses` instance for creating new objects.
    """

    def __init__(
        self,
        error_handler: ErrorHandler,
        pfdl_base_classes: PFDLBaseClasses = PFDLBaseClasses(),
    ) -> None:
        """Initialize the object.

        Args:
            error_handler: `ErrorHandler` instance for printing errors while visiting.
            pfdl_base_classes: `PFDLBaseClasses` instance for creating new objects.
        """
        self.error_handler: ErrorHandler = error_handler
        self.pfdl_base_classes: PFDLBaseClasses = pfdl_base_classes
        self.current_task: Task = None

    def visitProgram(self, ctx) -> Process:
        """Starts the visiting of the syntax tree of the given PFDL program."""
        process = Process()

        if ctx.children:
            for child in ctx.children:
                process_component = self.visit(child)

                if isinstance(process_component, self.pfdl_base_classes.get_class("Struct")):
                    if process_component.name not in process.structs:
                        process.structs[process_component.name] = process_component
                    else:
                        error_msg = (
                            f"A Struct with the name '{process_component.name}' "
                            "is already defined"
                        )
                        self.error_handler.print_error(error_msg, context=child)
                elif isinstance(process_component, self.pfdl_base_classes.get_class("Task")):
                    if process_component.name not in process.tasks:
                        process.tasks[process_component.name] = process_component
                    else:
                        error_msg = (
                            f"A Task with the name '{process_component.name}' " "is already defined"
                        )
                        self.error_handler.print_error(error_msg, context=child)
                elif isinstance(process_component, self.pfdl_base_classes.get_class("Instance")):
                    if process_component.name not in process.tasks:
                        process.instances[process_component.name] = process_component
                    else:
                        error_msg = (
                            f"An instance with the name '{process_component.name}' "
                            "is already defined"
                        )
                        self.error_handler.print_error(error_msg, context=child)

        # perform additional steps after visiting the syntax tree
        self.execute_additional_tasks(process)

        return process

    def execute_additional_tasks(self, process: Process) -> None:
        """Runs additional parsing methods with full information."""

        # add instances to task variables so they can be used in expressions
        self.addInstancesToAllTasks(process)

        # add attributes to the structs that are inherited from all parent structs
        self.add_inherited_attributes_to_structs(process)

    def add_inherited_attributes_to_structs(self, process: Process) -> None:
        """Tries to add attributes inherited from the respective parents to all child structs.

        Throws an error if one parent struct name is found to be invalid.
        """
        for struct_name, struct in process.structs.items():
            parent_struct_attributes, invalid_parent_name = helpers.get_parent_struct_attributes(
                struct_name, process.structs
            )
            if not invalid_parent_name:
                struct.attributes.update(parent_struct_attributes)
            else:
                error_msg = (
                    f"The Struct '{struct.name}' tries to inherit from an unknown Struct "
                    f"'{invalid_parent_name}'."
                )
                self.error_handler.print_error(error_msg, context=struct.context)

    def visitProgram_statement(self, ctx: PFDLParser.Program_statementContext):
        if not isinstance(ctx.children[0], TerminalNodeImpl):
            return self.visit(ctx.children[0])

    def addInstancesToAllTasks(self, process: Process) -> None:
        """Adds all instances to the variables of all tasks in the process.

        This method is necessary to use the instances in expressions.

        Args:
            process: The `Process` object containing all tasks and instances.
        """
        for instance in process.instances.values():
            for task in process.tasks.values():
                task.variables[instance.name] = instance.struct_name

    def visitStruct(self, ctx) -> Struct:
        struct = self.pfdl_base_classes.get_class("Struct")()
        struct.name = ctx.STARTS_WITH_UPPER_C_STR().getText()
        struct.context = ctx

        for variable_definition_ctx in ctx.variable_definition():
            identifier, variable_type = self.visitVariable_definition(variable_definition_ctx)
            struct.context_dict[identifier] = variable_definition_ctx

            if identifier not in struct.attributes:
                struct.attributes[identifier] = variable_type
            else:
                error_msg = (
                    f"An attribute with the name '{identifier}'"
                    "is already defined in the Struct '{struct.name}'"
                )
                self.error_handler.print_error(error_msg, context=variable_definition_ctx)

        if ctx.struct_id():
            struct.parent_struct_name = self.visitStruct_id(ctx.struct_id())

        return struct

    def visitStruct_id(self, ctx: PFDLParser.Struct_idContext) -> str:
        return ctx.children[0].getText()

    def visitTask(self, ctx) -> Task:
        task = self.pfdl_base_classes.get_class("Task")()
        task.name = ctx.STARTS_WITH_LOWER_C_STR().getText()
        task.context = ctx

        self.current_task = task

        if ctx.task_in():
            task.input_parameters = self.visitTask_in(ctx.task_in())
            task.context_dict[IN_KEY] = ctx.task_in()

        for statement_ctx in ctx.taskStatement():
            statement = self.visitTaskStatement(statement_ctx)
            task.statements.append(statement)
        if ctx.task_out():
            task.output_parameters = self.visitTask_out(ctx.task_out())
            task.context_dict[OUT_KEY] = ctx.task_out()

        return task

    def visitInstance(self, ctx: PFDLParser.InstanceContext) -> Instance:
        instance_name = ctx.STARTS_WITH_LOWER_C_STR().getText()
        struct_name = self.visitStruct_id(ctx.struct_id())
        instance = self.pfdl_base_classes.get_class("Instance")(
            name=instance_name, struct_name=struct_name, context=ctx
        )
        self.current_program_component = instance
        for attribute_assignment_ctx in ctx.attribute_assignment():
            attribute_name, attribute_value = self.visitAttribute_assignment(
                attribute_assignment_ctx
            )
            # JSON value
            if isinstance(attribute_value, Dict):
                attribute_value = self.pfdl_base_classes.get_class("Instance").from_json(
                    attribute_value,
                    self.error_handler,
                    ctx,
                    self.pfdl_base_classes.get_class("Instance"),
                )
            instance.attributes[attribute_name] = attribute_value
            instance.attribute_contexts[attribute_name] = attribute_assignment_ctx

        return instance

    def visitAttribute_assignment(
        self, ctx: PFDLParser.Attribute_assignmentContext
    ) -> Tuple[List[str], Union[str, Dict]]:
        value = None
        if ctx.value():
            value = self.visitValue(ctx.value())
            value = helpers.cast_element(value)
        else:
            value = self.visitJson_object(ctx.json_object())
        return (ctx.STARTS_WITH_LOWER_C_STR().getText(), value)

    def visitTask_in(self, ctx: PFDLParser.Task_inContext) -> Dict[str, Union[str, Array]]:
        input_parameters = OrderedDict()
        for variable_definition_context in ctx.variable_definition():
            identifier, variable_type = self.visitVariable_definition(variable_definition_context)
            self.current_task.variables[identifier] = variable_type

            if identifier not in input_parameters:
                input_parameters[identifier] = variable_type
            else:
                error_msg = f"There is already a input paramter with the name '{identifier} '."
                self.error_handler.print_error(error_msg, context=variable_definition_context)
                pass
        return input_parameters

    def visitTask_out(self, ctx: PFDLParser.Task_outContext) -> List[str]:
        output_parameters = []
        for child in ctx.STARTS_WITH_LOWER_C_STR():
            output_parameters.append(child.getText())
        return output_parameters

    def visitStatement(
        self, ctx: PFDLParser.StatementContext
    ) -> Union[Service, TaskCall, WhileLoop, CountingLoop, Condition]:
        statement = None
        if ctx.service_call():
            statement = self.visitService_call(ctx.service_call())
        elif ctx.task_call():
            statement = self.visitTask_call(ctx.task_call())
        elif ctx.parallel():
            statement = self.visitParallel(ctx.parallel())
        elif ctx.while_loop():
            statement = self.visitWhile_loop(ctx.while_loop())
        elif ctx.counting_loop():
            statement = self.visitCounting_loop(ctx.counting_loop())
        else:
            statement = self.visitCondition(ctx.condition())

        return statement

    def visitService_call(self, ctx: PFDLParser.Service_callContext) -> Service:
        service = self.pfdl_base_classes.get_class("Service")()
        service.context = ctx

        service.name = ctx.STARTS_WITH_UPPER_C_STR().getText()

        input_params = []
        output_params = OrderedDict()
        if ctx.call_input():
            input_params = self.visitCall_input(ctx.call_input())
        if ctx.call_output():
            output_params = self.visitCall_output(ctx.call_output())

        service.context_dict[IN_KEY] = ctx.call_input()
        service.context_dict[OUT_KEY] = ctx.call_output()
        service.input_parameters = input_params
        service.output_parameters = output_params

        return service

    def visitCall_input(
        self, ctx: PFDLParser.Call_inputContext
    ) -> List[Union[str, List[str], Struct]]:
        input_params = []
        for child in ctx.parameter():
            parameter = self.visitParameter(child)
            input_params.append(parameter)
        for child in ctx.struct_initialization():
            struct = self.visitStruct_initialization(child)
            input_params.append(struct)
        return input_params

    def visitCall_output(self, ctx: PFDLParser.Call_outputContext) -> Dict[str, Union[str, Array]]:
        output_parameter = OrderedDict()
        for variable_definition_ctx in ctx.variable_definition():
            identifier, variable_type = self.visitVariable_definition(variable_definition_ctx)

            if identifier not in output_parameter:
                self.current_task.variables[identifier] = variable_type
                output_parameter[identifier] = variable_type
            else:
                error_msg = f"There is already a output parameter with the name '{identifier}'."
                self.error_handler.print_error(error_msg, context=variable_definition_ctx)
        return output_parameter

    def visitParameter(self, ctx: PFDLParser.ParameterContext) -> Union[str, List[str]]:
        if ctx.STARTS_WITH_LOWER_C_STR():
            return ctx.STARTS_WITH_LOWER_C_STR().getText()
        return self.visitAttribute_access(ctx.attribute_access())

    def visitStruct_initialization(self, ctx: PFDLParser.Struct_initializationContext) -> Struct:
        json_string = ctx.json_object().getText()

        struct = self.pfdl_base_classes.get_class("Struct").from_json(
            json_string, self.error_handler, ctx.json_object()
        )
        struct.name = ctx.STARTS_WITH_UPPER_C_STR().getText()
        struct.context = ctx
        return struct

    def visitTask_call(self, ctx: PFDLParser.Task_callContext) -> TaskCall:
        task_call = self.pfdl_base_classes.get_class("TaskCall")()
        task_call.name = ctx.STARTS_WITH_LOWER_C_STR().getText()
        task_call.context = ctx

        input_params = []
        output_params = OrderedDict()
        if ctx.call_input():
            input_params = self.visitCall_input(ctx.call_input())
        if ctx.call_output():
            output_params = self.visitCall_output(ctx.call_output())

        task_call.context_dict[IN_KEY] = ctx.call_input()
        task_call.context_dict[OUT_KEY] = ctx.call_output()

        task_call.input_parameters = input_params
        task_call.output_parameters = output_params

        return task_call

    def visitParallel(self, ctx: PFDLParser.ParallelContext) -> Parallel:
        parallel = self.pfdl_base_classes.get_class("Parallel")()
        parallel.context = ctx
        for task_call_context in ctx.task_call():
            task_call = self.visitTask_call(task_call_context)
            parallel.task_calls.append(task_call)
        return parallel

    def visitWhile_loop(self, ctx: PFDLParser.While_loopContext) -> WhileLoop:
        while_loop = self.pfdl_base_classes.get_class("WhileLoop")()
        while_loop.context = ctx

        while_loop.expression = self.visitExpression(ctx.expression())

        for statement_ctx in ctx.statement():
            statement = self.visitStatement(statement_ctx)
            while_loop.statements.append(statement)
        return while_loop

    def visitCounting_loop(self, ctx: PFDLParser.Counting_loopContext) -> CountingLoop:
        counting_loop = self.pfdl_base_classes.get_class("CountingLoop")()
        counting_loop.context = ctx

        counting_loop.counting_variable = ctx.STARTS_WITH_LOWER_C_STR().getText()

        if ctx.attribute_access():
            counting_loop.limit = self.visitAttribute_access(ctx.attribute_access())
        else:
            counting_loop.limit = int(ctx.INTEGER().getText())

        # check if parallel keyword is there
        if ctx.PARALLEL():
            counting_loop.parallel = True
        for statement_ctx in ctx.statement():
            statement = self.visitStatement(statement_ctx)
            counting_loop.statements.append(statement)
        return counting_loop

    def visitCondition(self, ctx: PFDLParser.ConditionContext) -> Condition:
        condition_statement = self.pfdl_base_classes.get_class("Condition")()
        condition_statement.context = ctx

        condition_statement.expression = self.visitExpression(ctx.expression())
        condition_statement.passed_stmts = self.visitCondition_passed(ctx.condition_passed())

        if ctx.condition_failed():
            condition_statement.failed_stmts = self.visitCondition_failed(ctx.condition_failed())
        return condition_statement

    def visitCondition_passed(
        self, ctx: PFDLParser.Condition_passedContext
    ) -> List[Union[Service, TaskCall, WhileLoop, CountingLoop, Condition]]:
        statements = []
        for child in ctx.statement():
            statement = self.visitStatement(child)
            statements.append(statement)
        return statements

    def visitCondition_failed(
        self, ctx: PFDLParser.Condition_failedContext
    ) -> List[Union[Service, TaskCall, WhileLoop, CountingLoop, Condition]]:
        statements = []
        for child in ctx.statement():
            statement = self.visitStatement(child)
            statements.append(statement)
        return statements

    def visitVariable_definition(
        self, ctx: PFDLParser.Variable_definitionContext
    ) -> Tuple[str, Union[str, Array]]:
        identifier = ctx.STARTS_WITH_LOWER_C_STR().getText()
        variable_type = self.visitVariable_type(ctx.variable_type())

        return (identifier, variable_type)

    def visitVariable_type(self, ctx: PFDLParser.Variable_typeContext) -> Union[str, Array]:
        variable_type = self.visitPrimitive(ctx.primitive())

        if ctx.array():
            array = self.initializeArray(ctx.array(), variable_type)
            variable_type = array

        return variable_type

    def visitPrimitive(self, ctx: PFDLParser.PrimitiveContext):
        return ctx.getText()

    def initializeArray(self, array_ctx: PFDLParser.ArrayContext, variable_type: str) -> Array:
        array = self.pfdl_base_classes.get_class("Array")()
        array.type_of_elements = variable_type
        array.context = array_ctx
        length = self.visitArray(array_ctx)
        if not isinstance(length, int):
            self.error_handler.print_error(
                "Array length has to be specified by an integer", syntax_error=True
            )
        else:
            array.length = length

        return array

    def visitAttribute_access(self, ctx: PFDLParser.Attribute_accessContext) -> List[str]:
        access_list = []

        for child in ctx.children:
            if child.getText() != ".":
                access_list.append(child.getText())
        return access_list

    def visitValue(self, ctx: PFDLParser.ValueContext) -> str:
        if ctx.attribute_access():
            return self.visitAttribute_access(ctx.attribute_access())
        return ctx.children[0].getText()

    def visitArray(self, ctx: PFDLParser.ArrayContext) -> Union[int, str]:
        if ctx.INTEGER():
            return int(ctx.INTEGER().getText())
        if ctx.STARTS_WITH_LOWER_C_STR():
            return ctx.STARTS_WITH_LOWER_C_STR().getText()
        return -1  # No length specified

    def visitExpression(self, ctx: PFDLParser.ExpressionContext) -> Dict:
        length = len(ctx.children)

        if length == 1:
            ele = self.get_content(ctx.children[0])
            if isinstance(ele, List):
                return ele
            elif not helpers.is_string(ele):
                # strings should not appear here
                casted_element = helpers.cast_element(ele)
                # check if ele is a primitve datatype (number or bool)
                if casted_element != ele:
                    return casted_element
        if length == 2:
            un_op = self.get_content(ctx.children[0])
            ele = self.get_content(ctx.children[1])
            return dict(unOp=un_op, value=ele)

        if length == 3:
            left = self.get_content(ctx.children[0])
            bin_op = self.get_content(ctx.children[1])
            right = self.get_content(ctx.children[2])
            return dict(binOp=bin_op, left=left, right=right)

        return None

    def get_content(self, child) -> Union[str, List]:
        ele = self.visit(child)

        if ele is None:
            ele = child.getText()
        return ele

    def visitBinOperation(self, ctx: PFDLParser.BinOperationContext) -> str:
        return ctx.children[0].getText()

    def visitUnOperation(self, ctx: PFDLParser.UnOperationContext) -> str:
        return ctx.children[0].getText()
