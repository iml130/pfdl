# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains the Condition class."""

# standard libraries
from dataclasses import dataclass
from typing import Dict, List, Union

# 3rd party libraries
from antlr4.ParserRuleContext import ParserRuleContext

# local sources
from pfdl_scheduler.model.task_call import TaskCall
from pfdl_scheduler.model.service import Service


@dataclass
class Condition:
    """Represents a conditional statement in the PFDL.

    A Condition consists of a boolean expression which has to be satisfied in order
    to execute the statements in the Passed block. Otherwise the statements in the Failed block
    will be executed.

    Attributes:
        expression: Boolean expression in form of a dict (see Visitor for the dict structure).
        passed_stmts: List of statements which are executed when the expression is satisfied.
        failed_stmts: List of statements which are executed when the expression is not satisfied.
        context: ANTLR context object of this class.
        context_dict: Maps other attributes with ANTLR context objects.
    """

    def __init__(
        self,
        expression: Dict = None,
        passed_stmts: List[Union[Service, TaskCall, "Loop", "Condition"]] = None,
        failed_stmts: List[Union[Service, TaskCall, "Loop", "Condition"]] = None,
        context: ParserRuleContext = None,
    ) -> None:
        """Initialize the object.

        Args:
            expression: Boolean expression in form of a dict (see Visitor for the dict structure).
            passed_stmts: List of statements which are executed when the expression is satisfied.
            failed_stmts: List of statements which are executed when the expression is not satisfied.
            context: ANTLR context object of this class.
        """
        self.expression: Dict = expression

        if passed_stmts:
            self.passed_stmts: List[Union[Service, TaskCall, "Loop", "Condition"]] = passed_stmts
        else:
            self.passed_stmts: List[Union[Service, TaskCall, "Loop", "Condition"]] = []

        if failed_stmts:
            self.failed_stmts: List[Union[Service, TaskCall, "Loop", "Condition"]] = failed_stmts
        else:
            self.failed_stmts: List[Union[Service, TaskCall, "Loop", "Condition"]] = []

        self.context: ParserRuleContext = context
        self.context_dict: Dict = {}
