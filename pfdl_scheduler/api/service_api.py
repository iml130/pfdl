# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT
"""Contains the ServiceAPI class."""
# standard libraries
import copy
from typing import List, Union
from uuid import uuid4
from dataclasses import dataclass

# local sources
from pfdl_scheduler.api.task_api import TaskAPI
from pfdl_scheduler.model.service import Service
from pfdl_scheduler.model.struct import Struct


@dataclass
class ServiceAPI:
    """Represents a called Service.
    Represents a Service or Service Call in the langauge which can be mapped to a real
    service that can be executed.
    Attributes:
        service: A description of the called Service.
        task_context: A TaskAPI representaiton of the Task from which the service was called.
        uuid: A UUID4 which is generated at object creation and is used in the scheduling.
        in_loop: A boolean indicating whether the Service was called within a loop.
    """

    def __init__(
        self,
        service: Service,
        task_context: TaskAPI,
        uuid: str = "",
        in_loop: bool = False,
    ) -> None:
        """Initialize the object.
        Args:
            service: A description of the called Service.
            task_context: A TaskAPI representaiton of the Task from which the service was called.
            uuid: A UUID4 which is generated at object creation and is used in the scheduling.
            in_loop: A boolean indicating whether the Service was called within a loop.
        """
        if uuid == "":
            self.uuid: str = str(uuid4())
        else:
            self.uuid: str = uuid
        self.in_loop: bool = in_loop
        self.service: Service = service
        self.task_context: TaskAPI = task_context
        self.input_parameters: List[Union[str, List[str], Struct]] = copy.deepcopy(
            service.input_parameters
        )
