# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains the WhileLoop class."""

# standard libraries
from dataclasses import dataclass
from typing import Dict, List, Union

# 3rd party libraries
from antlr4.ParserRuleContext import ParserRuleContext

# local sources
from pfdl_scheduler.model.loop import Loop
from pfdl_scheduler.model.service import Service
from pfdl_scheduler.model.task_call import TaskCall
from pfdl_scheduler.model.condition import Condition


@dataclass
class WhileLoop(Loop):
    """Represents a While Loop in the PFDL.

    Loops until conditional statement (expression) is satisfied.

    Attributes:
        statements: List of statements inside the loop body.
        expression: Boolean expression in form of a dict.
        context: ANTLR context object of this class.
        context_dict: Maps other attributes with ANTLR context objects.
    """

    def __init__(
        self,
        statements: List[Union[Service, TaskCall, Loop, Condition]] = None,
        expression: Dict = None,
        context: ParserRuleContext = None,
    ) -> None:
        """Initialize the object.

        Args:
            statements: List of statements inside the loop body.
            expression: Boolean expression in form of a dict.
            context: ANTLR context object of this class.
        """
        Loop.__init__(self, statements, context)

        if expression:
            self.expression: Dict = expression
        else:
            self.expression: Dict = {}
