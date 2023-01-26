# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains the TaskAPI class."""

# standard libraries
import copy
from typing import List, Union
from dataclasses import dataclass
from uuid import uuid4
from pfdl_scheduler.model.struct import Struct

# local sources
from pfdl_scheduler.model.task import Task
from pfdl_scheduler.model.task_call import TaskCall


@dataclass
class TaskAPI:
    """Represents a called Task.

    Represents a specific entity of a called Task. It combines the information of the Task itself
    and the parameters of the call. A TaskAPI object is used in the task started and finished callback
    which are called by the scheduler.

    Attributes:
        task: A description of the called Task.
        task_context: A TaskAPI representaiton of the Task from which the called task was invoked.
        uuid: A UUID4 which is generated at object creation and is used in the scheduling.
        task_call: Information about the input and output parameters of the called Task.
        in_loop: A boolean indicating whether the Task was called within a loop.
    """

    def __init__(
        self,
        task: Task,
        task_context: "TaskAPI",
        uuid: str = "",
        task_call: TaskCall = None,
        in_loop: bool = False,
    ) -> None:
        """Initialize the object.

        Args:
            task: A description of the called Task.
            task_context: A TaskAPI representaiton of the Task from which the called task was invoked.
            uuid: A UUID4 which is generated at object creation and is used in the scheduling.
            task_call: Information about the input and output parameters of the called Task.
            in_loop: A boolean indicating whether the Task was called within a loop.
        """
        if uuid == "":
            self.uuid: str = str(uuid4())
        else:
            self.uuid: str = uuid
        self.task: Task = task
        self.task_context: TaskAPI = task_context
        self.task_call: TaskCall = task_call

        if task_call:
            self.input_parameters: List[Union[str, List[str], Struct]] = copy.deepcopy(
                task_call.input_parameters
            )
        else:
            self.input_parameters: List[Union[str, List[str], Struct]] = []
        self.in_loop: bool = in_loop
