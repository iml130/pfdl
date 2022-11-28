# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains the Loop class."""

# standard libraries
from dataclasses import dataclass
from typing import Dict, List, Union

# 3rd party libraries
from antlr4.ParserRuleContext import ParserRuleContext

# local sources
from pfdl_scheduler.model.service import Service
from pfdl_scheduler.model.task_call import TaskCall
from pfdl_scheduler.model.condition import Condition


@dataclass
class Loop:
    """The base class for the PFDL loops.

    Attributes:
        statements: List of statements inside the loop body.
        context: ANTLR context object of this class.
        context_dict: Maps other attributes with ANTLR context objects.
    """

    def __init__(
        self,
        statements: List[Union[Service, TaskCall, "Loop", Condition]] = None,
        context: ParserRuleContext = None,
    ) -> None:
        """Initialize the object.

        Args:
            statements: List of statements inside the loop body.
            context: ANTLR context object of this class.
        """
        if statements:
            self.statements: List[Union[Service, TaskCall, "Loop", Condition]] = statements
        else:
            self.statements: List[Union[Service, TaskCall, "Loop", Condition]] = []
        self.context: ParserRuleContext = context
        self.context_dict: Dict = {}
