# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains the CountingLoop class."""

# standard libraries
from dataclasses import dataclass
from typing import List, Union
import uuid
import hashlib

# 3rd party libraries
from antlr4.ParserRuleContext import ParserRuleContext

# local sources
from pfdl_scheduler.model.loop import Loop
from pfdl_scheduler.model.service import Service
from pfdl_scheduler.model.task_call import TaskCall
from pfdl_scheduler.model.condition import Condition


@dataclass
class CountingLoop(Loop):
    """Represents a Counting Loop in the PFDL.

    Counting loops count a variable from an initial value to a given upper limit.
    If the parallel keyword was used, this loop executes the statements in the loop body
    in parallel as many times as the loop would iterate.

    Attributes:
        statements: List of statements inside the loop body.
        context: ANTLR context object of this class.
        context_dict: Maps other attributes with ANTLR context objects.
        counting_variable: Name of the variable which is counted in the loop.
        limit: Integer for the upper limit.
        parallel: A boolean indicating if the loop is a parallel loop or not.
    """

    def __init__(
        self,
        statements: List[Union[Service, TaskCall, Loop, Condition]] = None,
        counting_variable: str = "",
        limit: str = "",
        parallel: bool = False,
        context: ParserRuleContext = None,
    ) -> None:
        """Initialize the object.

        Args:
            statements: List of statements inside the loop body.
            counting_variable: Name of the variable which is counted in the loop.
            limit: Integer for the upper limit.
            parallel: A boolean indicating if the loop is a parallel loop or not.
            context: ANTLR context object of this class.
        """
        Loop.__init__(self, statements, context)
        self.counting_variable: str = counting_variable
        self.limit: str = limit
        self.parallel: bool = parallel
        self.uuid = str(uuid.uuid4())

    def __hash__(self) -> int:
        return int(uuid.UUID(self.uuid))
