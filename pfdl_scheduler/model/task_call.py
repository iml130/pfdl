# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains the TaskCall class."""

# standard libraries
from dataclasses import dataclass
from typing import Dict, List, Union

# 3rd party libraries
from antlr4.ParserRuleContext import ParserRuleContext

# local sources
from pfdl_scheduler.model.array import Array
from pfdl_scheduler.model.struct import Struct


@dataclass
class TaskCall:
    """Represents a TaskCall in the PFDL.

    Provides information about the name and call parameters
    of a Task which is called within another Task.

    Attributes:
        name: A string representing the name of the TaskCall.
        input_parameters: List of input parameters of the TaskCall.
        output_parameters: List of output parameters of the TaskCall.
        context: ANTLR context object of this class.
        context_dict: Maps other attributes with ANTLR context objects.
    """

    def __init__(
        self,
        name: str = "",
        input_parameters: List[Union[str, List[str], Struct]] = None,
        output_parameters: Dict[str, Union[str, Array]] = None,
        context: ParserRuleContext = None,
    ) -> None:
        """Initialize the object.

        Args:
            name: A string representing the name of the TaskCall.
            input_parameters: List of input parameters of the TaskCall.
            output_parameters: List of output parameters of the TaskCall.
            context: ANTLR context object of this class.
        """
        self.name: str = name

        if input_parameters:
            self.input_parameters: List[Union[str, List[str], Struct]] = input_parameters
        else:
            self.input_parameters: List[Union[str, List[str], Struct]] = []

        if output_parameters:
            self.output_parameters: Dict[str, Union[str, Array]] = output_parameters
        else:
            self.output_parameters: Dict[str, Union[str, Array]] = {}

        self.context: ParserRuleContext = context
        self.context_dict: Dict = {}
