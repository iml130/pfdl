# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains the Process class."""

# standard libraries
from dataclasses import dataclass
from typing import Dict

# local sources
from pfdl_scheduler.model.struct import Struct
from pfdl_scheduler.model.task import Task


@dataclass
class Process:
    """Represents a production process described in a PFDL file.

    A Process consists of multiple Structs and Tasks. A Process object gets created after the
    visitor traverses the syntax tree.

    Attributes:
        structs: A dict for mapping the Struct names to the Struct objects.
        task: A dict for mapping the Task names to the Task objects.
    """

    def __init__(self, structs: Dict[str, Struct] = None, tasks: Dict[str, Task] = None) -> None:
        """Initialize the object.

        Args:
            structs: A dict for mapping the Struct names to the Struct objects.
            tasks: A dict for mapping the Task names to the Task objects.
        """
        if structs:
            self.structs: Dict[str, Struct] = structs
        else:
            self.structs: Dict[str, Struct] = {}
        if tasks:
            self.tasks: Dict[str, Task] = tasks
        else:
            self.tasks: Dict[str, Task] = {}
