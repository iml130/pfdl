# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains the Service class."""

# standard libraries
from dataclasses import dataclass
from typing import Dict, List, OrderedDict, Union

# 3rd party libraries
from antlr4.ParserRuleContext import ParserRuleContext

# local sources
from pfdl_scheduler.model.struct import Struct
from pfdl_scheduler.model.array import Array


@dataclass
class Service:
    """Represents a Service or Service Call in the PFDL.

    Represents a Service or Service Call in the langauge which can be mapped to a real
    service that can be executed.

    Attributes:
        name: A string representing the name of the Service.
        input_parameters: List of input parameters of the Service.
        output_parameters: List of output parameters of the Service.
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
            name: A string representing the name of the Service.
            input_parameters: List of input parameters of the Service.
            output_parameters: List of output parameters of the Service.
            context: ANTLR context object of this class.
        """
        self.name: str = name

        if input_parameters:
            self.input_parameters: List[Union[str, List[str], Struct]] = input_parameters
        else:
            self.input_parameters: List[Union[str, List[str], Struct]] = []

        if output_parameters:
            self.output_parameters: OrderedDict[str, Union[str, Array]] = output_parameters
        else:
            self.output_parameters: OrderedDict[str, Union[str, Array]] = OrderedDict()

        self.context: ParserRuleContext = context
        self.context_dict: Dict = {}
