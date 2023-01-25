# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains PFDLTreeVisitor class."""

# standard libraries
from typing import Dict, List, OrderedDict, Tuple, Union
from pfdl_scheduler.utils import helpers
from pfdl_scheduler.model.parallel import Parallel

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
    """

    def __init__(self, error_handler: ErrorHandler) -> None:
        """Initialize the object.

        Args:
            error_handler: ErrorHandler instance for printing errors while visiting.
        """
        self.error_handler: ErrorHandler = error_handler
        self.current_task: Task = None

    def visitProgram(self, ctx) -> Process:
        """Starts the visiting of the syntax tree of the given PFDL program."""
        process = Process()

        if ctx.children:
            for child in ctx.children:
                process_component = self.visit(child)

                if isinstance(process_component, Struct):
                    if process_component.name not in process.structs:
                        process.structs[process_component.name] = process_component
                    else:
                        error_msg = (
                            f"A Struct with the name '{process_component.name}' "
                            "is already defined"
                        )
                        self.error_handler.print_error(error_msg, context=child)
                elif isinstance(process_component, Task):
                    if process_component.name not in process.tasks:
                        process.tasks[process_component.name] = process_component
                    else:
                        error_msg = (
                            f"A Task with the name '{process_component.name}' " "is already defined"
                        )
                        self.error_handler.print_error(error_msg, context=child)
        return process

    def visitStruct(self, ctx) -> Struct:
        struct = Struct()
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
        return struct

    def visitTask(self, ctx) -> Task:
        task = Task()
        task.name = ctx.STARTS_WITH_LOWER_C_STR().getText()
        task.context = ctx

        self.current_task = task

        if ctx.task_in():
            task.input_parameters = self.visitTask_in(ctx.task_in())
            task.context_dict[IN_KEY] = ctx.task_in()

        for statement_ctx in ctx.statement():
            statement = self.visitStatement(statement_ctx)
            task.statements.append(statement)
        if ctx.task_out():
            task.output_parameters = self.visitTask_out(ctx.task_out())
            task.context_dict[OUT_KEY] = ctx.task_out()

        return task

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
        service = Service()
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

        struct = Struct.from_json(json_string, self.error_handler, ctx.json_object())
        struct.name = ctx.STARTS_WITH_UPPER_C_STR().getText()
        struct.context = ctx
        return struct

    def visitTask_call(self, ctx: PFDLParser.Task_callContext) -> TaskCall:
        task_call = TaskCall()
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
        parallel = Parallel()
        parallel.context = ctx
        for task_call_context in ctx.task_call():
            task_call = self.visitTask_call(task_call_context)
            parallel.task_calls.append(task_call)
        return parallel

    def visitWhile_loop(self, ctx: PFDLParser.While_loopContext) -> WhileLoop:
        while_loop = WhileLoop()
        while_loop.context = ctx

        while_loop.expression = self.visitExpression(ctx.expression())

        for statement_ctx in ctx.statement():
            statement = self.visitStatement(statement_ctx)
            while_loop.statements.append(statement)
        return while_loop

    def visitCounting_loop(self, ctx: PFDLParser.Counting_loopContext) -> CountingLoop:
        counting_loop = CountingLoop()
        counting_loop.context = ctx

        counting_loop.counting_variable = ctx.STARTS_WITH_LOWER_C_STR().getText()
        counting_loop.limit = self.visitAttribute_access(ctx.attribute_access())

        # check if parallel keyword is there
        if ctx.PARALLEL():
            counting_loop.parallel = True
        for statement_ctx in ctx.statement():
            statement = self.visitStatement(statement_ctx)
            counting_loop.statements.append(statement)
        return counting_loop

    def visitCondition(self, ctx: PFDLParser.ConditionContext) -> Condition:
        condition_statement = Condition()
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

        variable_type = self.visitPrimitive(ctx.primitive())

        if ctx.array():
            array = Array()
            array.type_of_elements = variable_type
            array.context = ctx.array()
            length = self.visitArray(ctx.array())
            if not isinstance(length, int):
                self.error_handler.print_error(
                    "Array length has to be specified by an integer", syntax_error=True
                )
            else:
                array.length = length

            variable_type = array

        return (identifier, variable_type)

    def visitPrimitive(self, ctx: PFDLParser.PrimitiveContext):
        return ctx.getText()

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
            if helpers.is_int(ele):
                return int(ele)
            if helpers.is_float(ele):
                return float(ele)
            if helpers.is_boolean(ele):
                return ele == "true"
        if length == 2:
            un_op = self.get_content(ctx.children[0])
            ele = self.get_content(ctx.children[1])
            return dict(unop=un_op, value=ele)

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
