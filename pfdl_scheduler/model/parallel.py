# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains the Parallel class."""

# standard libraries
from dataclasses import dataclass
from typing import Dict, List

# 3rd party libraries
from antlr4.ParserRuleContext import ParserRuleContext

# local sources
from pfdl_scheduler.model.task_call import TaskCall


@dataclass
class Parallel:
    """Represents a Parallel statement in the PFDL.

    Each task within this instruction is executed in parallel with the calling task.
    When all parallel tasks are finished, the calling task continues its execution.

    Attributes:
        task_calls: List of Task Calls in the Parallel statement.
        context: ANTLR context object of this class.
        context_dict: Maps other attributes with ANTLR context objects.
    """

    def __init__(
        self, task_calls: List[TaskCall] = None, context: ParserRuleContext = None
    ) -> None:
        """Initialize the object.

        Args:
            task_calls: List of Task Calls in the Parallel statement.
            context: ANTLR context object of this class.
        """
        if task_calls:
            self.task_calls: List[TaskCall] = task_calls
        else:
            self.task_calls: List[TaskCall] = []
        self.context: ParserRuleContext = context
        self.context_dict: Dict = {}
