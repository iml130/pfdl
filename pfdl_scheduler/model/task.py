# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains the Task class."""

# standard libraries
from dataclasses import dataclass
from typing import Dict, OrderedDict, Union, List

# 3rd party libraries
from antlr4.ParserRuleContext import ParserRuleContext

# local sources
from pfdl_scheduler.model.service import Service
from pfdl_scheduler.model.task_call import TaskCall
from pfdl_scheduler.model.condition import Condition
from pfdl_scheduler.model.array import Array
from pfdl_scheduler.model.while_loop import Loop


@dataclass
class Task:
    """Represents a Task in the PFDL.

    A Task contains statements which are executed sequentially.
    It is possible to define input and output parameters of a Task.

    Attributes:
        name: A string representing the name of the Task.
        statements: List of statements which are executed sequentially.
        variables: Dict for mapping variable names with their values.
        input_parameters: OrderedDict for mapping input parameter names with their values.
        output_parameters: List of variable names as output parameters.
        context: ANTLR context object of this class.
        context_dict: Maps other attributes with ANTLR context objects.
    """

    def __init__(
        self,
        name: str = "",
        statements: List[Union[Service, TaskCall, Loop, Condition]] = None,
        variables: Dict[str, Union[str, Array]] = None,
        input_parameters: OrderedDict[str, Union[str, Array]] = None,
        output_parameters: List[str] = None,
        context: ParserRuleContext = None,
    ) -> None:
        """Initialize the object.

        Args:
            name: A string representing the name of the Task.
            statements: List of statements which are executed sequentially.
            variables: Dict for mapping variable names with their values.
            input_parameters: OrderedDict for mapping input parameter names with their values.
            output_parameters: List of variable names as output parameters.
            context: ANTLR context object of this class.
        """
        self.name: str = name

        if statements:
            self.statements: List[Union[Service, TaskCall, Loop, Condition]] = statements
        else:
            self.statements: List[Union[Service, TaskCall, Loop, Condition]] = []

        if variables:
            self.variables: Dict[str, Union[str, Array]] = variables
        else:
            self.variables: Dict[str, Union[str, Array]] = {}

        if input_parameters:
            self.input_parameters: OrderedDict[str, Union[str, Array]] = input_parameters
        else:
            self.input_parameters: OrderedDict[str, Union[str, Array]] = {}

        if output_parameters:
            self.output_parameters: List[str] = output_parameters
        else:
            self.output_parameters: List[str] = []

        self.context: ParserRuleContext = context
        self.context_dict: Dict = {}
