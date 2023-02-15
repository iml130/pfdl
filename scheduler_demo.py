# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""This file contains an interface to demonstrate the use of the PFDL Scheduler."""

# standard libraries
import argparse
from typing import Any
import requests
import base64
import logging
from datetime import datetime

# local sources
from pfdl_scheduler.api.service_api import ServiceAPI
from pfdl_scheduler.api.observer_api import NotificationType, Observer
from pfdl_scheduler.api.task_api import TaskAPI
from pfdl_scheduler.model.struct import Struct
from pfdl_scheduler.scheduler import Scheduler, Event

# do not log requests entries if it is lesser than a warning
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


class PetriNetObserver(Observer):
    """PetriNetObserver for receiving infos about a change of the PetriNet.

    The Observer will send a post request to the dashboard with the Petri Net image
    encoded with base64.
    """

    def __init__(self, host: str):
        self.host = host

    def update(self, notification_type: NotificationType, data: Any) -> None:
        if notification_type == NotificationType.PETRI_NET:
            encoded_string = ""
            with open("temp/petri_net.png", "rb") as file:
                encoded_string = base64.b64encode(file.read())

            request_data = {
                "order_id": "8bf4eb6a-74df-427c-a475-532392465f70",
                "content": b"data:image/png;base64," + encoded_string,
                "type_pn": "png",
            }

            requests.post(url=self.host + "/petri_net", data=request_data)


class LogEntryObserver(Observer):
    """LogEntryObserver for receiving logging information from the Scheduler.

    LogLevels are based of https://docs.python.org/3/library/logging.html#logging-levels
    """

    def __init__(self, host: str = ""):
        logging.basicConfig(
            filename="temp/scheduler.log",
            encoding="utf-8",
            level=logging.DEBUG,
            filemode="w",
        )

        if host == "":
            self.dashboard_available: bool = False
        else:
            self.dashboard_available: bool = True
            self.host = host

    def update(self, notification_type: NotificationType, data: Any) -> None:
        if notification_type == NotificationType.LOG_ENTRY:
            log_entry = data[0]
            log_level = data[1]
            log_date = str(datetime.now())

            if self.dashboard_available:
                data = {
                    "order_id": "8bf4eb6a-74df-427c-a475-532392465f70",
                    "logDate": log_date,
                    "logLevel": log_level,
                    "logEntry": log_entry,
                }

                requests.post(url=self.host + "/log_entry", data=data)

            log_entry = log_date + ": " + log_entry
            logging.log(log_level, log_entry)


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
        "-dh", "--dashboard_host", type=str, help="the host address of the PFDL dashboard."
    )
    parser.add_argument(
        "--test_ids",
        action="store_true",
        help="services and tasks get test ids starting from 0.",
    )
    args = parser.parse_args()
    scheduler = Scheduler(args.file_path, args.test_ids)

    dashboard_host = ""
    if args.dashboard_host:
        dashboard_observer = PetriNetObserver(args.dashboard_host)
        scheduler.attach(dashboard_observer)
        dashboard_host = args.dashboard_host

    log_entry_observer = LogEntryObserver(dashboard_host)
    scheduler.attach(log_entry_observer)

    demo_interface = DemoInterface(scheduler)
    demo_interface.start()


if __name__ == "__main__":
    main()
