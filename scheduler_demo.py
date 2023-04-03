# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""This file contains an interface to demonstrate the use of the PFDL Scheduler."""

# standard libraries
import argparse

# local sources
from pfdl_scheduler.api.service_api import ServiceAPI
from pfdl_scheduler.api.task_api import TaskAPI
from pfdl_scheduler.model.struct import Struct
from pfdl_scheduler.scheduler import Scheduler, Event


class DemoInterface:
    """A dummy interface which demonstrates the use of the scheduler functions.

    At start the interface register its callback functions and variable access function
    to the scheduler. The callback functions provide a simple debug message to show
    the functionality of the scheduler.

    Attributes:
        scheduler: A Scheduler instance
        wetness: A dummy variable which is used in the PFDL examples
        parts_count: A dummy variable which is used in the PFDL examples
    """

    def __init__(self, scheduler: Scheduler) -> None:
        """Initialize the object"""
        self.scheduler: Scheduler = scheduler
        self.wetness: int = 11
        self.parts_count: int = 3

    def cb_task_started(self, task_api: TaskAPI) -> None:
        task_name = task_api.task.name
        task_id = task_api.uuid
        print("Task " + task_name + " with UUID '" + task_id + "' started")

    def cb_service_started(self, service_api: ServiceAPI) -> None:
        service_name = service_api.service.name
        service_id = service_api.uuid
        print("Service " + service_name + " with UUID '" + service_id + "' started")

    def cb_service_finished(self, service_api: ServiceAPI) -> None:
        service_name = service_api.service.name
        service_id = service_api.uuid
        print("Service " + service_name + " with UUID '" + service_id + "' finished")

    def cb_task_finished(self, task_api: TaskAPI) -> None:
        task_name = task_api.task.name
        task_id = task_api.uuid
        print("Task " + task_name + " with UUID '" + task_id + "' finished")

    def variable_access_function(self, var_name, task_context: TaskAPI) -> Struct:
        """Simulate a variable access function which returns a Struct variable.

        This dummy method simulates an access to variables from the PFDL. The returned structs
        are used in the examples folder.

        Returns:
            A struct variable corresponding to the given variable name in the given task context.
        """
        print("Request variable '" + var_name + "' from task with UUID '" + task_context.uuid + "'")
        dummy_struct = Struct()

        if var_name == "pr" or var_name == "dr":
            dummy_struct.attributes = {"wetness": self.wetness}
        elif var_name == "cr":
            dummy_struct.attributes = {"parts_count": self.parts_count}
        return dummy_struct

    def start(self):
        self.scheduler.register_callback_task_started(self.cb_task_started)
        self.scheduler.register_callback_service_started(self.cb_service_started)
        self.scheduler.register_callback_service_finished(self.cb_service_finished)
        self.scheduler.register_callback_task_finished(self.cb_task_finished)
        self.scheduler.register_variable_access_function(self.variable_access_function)
        self.scheduler.start()

        while self.scheduler.running:
            input_str = str(input("Wait for input:>"))
            splitted = input_str.split(",")
            service_id = splitted[0]
            event_type = splitted[1]

            event = Event(event_type=event_type, data={"service_id": service_id})
            self.scheduler.fire_event(event)


def main():
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument("file_path", type=str, help="the path for the PFDL file.")
    parser.add_argument(
        "--test_ids",
        action="store_true",
        help="services and tasks get test ids starting from 0.",
    )
    parser.add_argument(
        "-dh", "--dashboard_host", type=str, help="the host address of the PFDL dashboard."
    )
    args = parser.parse_args()

    dashboard_host_address = ""
    if args.dashboard_host:
        dashboard_host_address = args.dashboard_host
    scheduler = Scheduler(
        args.file_path, args.test_ids, dashboard_host_address=dashboard_host_address
    )

    demo_interface = DemoInterface(scheduler)
    demo_interface.start()


if __name__ == "__main__":
    main()
