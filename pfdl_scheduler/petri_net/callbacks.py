# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains the PetriNetCallbacks class."""

# standard libraries
from dataclasses import dataclass
from typing import Any, Callable, List

# local sources
from pfdl_scheduler.api.task_api import TaskAPI
from pfdl_scheduler.api.service_api import ServiceAPI
from pfdl_scheduler.model.condition import Condition
from pfdl_scheduler.model.counting_loop import CountingLoop
from pfdl_scheduler.model.while_loop import WhileLoop


@dataclass
class PetriNetCallbacks:
    """Internal callback functions that can be registered in the petri net.

    Attributes:
        task_started: Callback function which gets called when a task is started.
        service_started: Callback function which gets called when a service is started.
        service_finished: Callback function which gets called when a task is started.
        condition_started: Callback function which gets called when a task is started.
        while_loop_started: Callback function which gets called when a while loop is started.
        counting_loop_started: Callback function which gets called when a counting loop is started.
        parallel_loop_started: Callback function which gets called when a parallel loop is started.
        task_finished: Callback function which gets called when a task is finished.
    """

    task_started: Callable[[TaskAPI], Any] = None
    service_started: Callable[[ServiceAPI], Any] = None
    service_finished: Callable[[ServiceAPI], Any] = None
    condition_started: Callable[[Condition, str, str, TaskAPI], Any] = None
    while_loop_started: Callable[[WhileLoop, str, str, TaskAPI], Any] = None
    counting_loop_started: Callable[[CountingLoop, str, str, TaskAPI], Any] = None
    parallel_loop_started: Callable[[CountingLoop, TaskAPI, List, str, str], Any] = None
    task_finished: Callable[[TaskAPI], Any] = None
