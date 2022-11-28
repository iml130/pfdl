# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains the TaskCallbacks class."""

# standard libraries
from dataclasses import dataclass
from typing import Any, Callable, List

# local sources
from pfdl_scheduler.api.task_api import TaskAPI
from pfdl_scheduler.api.service_api import ServiceAPI


@dataclass
class TaskCallbacks:
    """Contains lists of callback functions that where registered in the scheduler.

    Attributes:
        task_started: A list of callback functions which get called when a task is started.
        service_started: A list of callback functions which get called when a service is started.
        service_finished: A list of callback functions which get called when a service is finished.
        task_finished: A list of callback functions which get called when a task is finished.
    """

    def __init__(self):
        """Initialize the object."""
        self.task_started: List[Callable[[TaskAPI], Any]] = []
        self.service_started: List[Callable[[ServiceAPI], Any]] = []
        self.service_finished: List[Callable[[ServiceAPI], Any]] = []
        self.task_finished: List[Callable[[TaskAPI], Any]] = []
