# Copyright The PFDL Contributors
#
# Licensed under the MIT License.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: MIT

"""Contains the start up script for the dashboard.

A program executed in the VS Code extension which
has a string containing a PFDL program as input.
"""

# standard libraries
import requests
from typing import Any
from datetime import datetime
import threading
import json
import queue

# local sources
from pfdl_scheduler.api.observer_api import NotificationType
from pfdl_scheduler.api.observer_api import Observer

# constants and variables
PETRI_NET_FILE_LOCATION = "temp/"  # the location of the petri net file
PETRI_NET_TYPE = "dot"  # the format of the sent petri net file

# http routes
ORDER_ROUTE = "/pfdl_order"
PETRI_NET_ROUTE = "/petri_net"
LOG_EVENT_ROUTE = "/log_event"

# order status
ORDER_STARTED = 2
ORDER_FINISHED = 4

message_queue = queue.Queue()
lock = threading.Lock()


def send_post_requests():
    while True:
        item = message_queue.get()
        requests.post(item[0], json.dumps(item[1]))
        message_queue.task_done()


class DashboardObserver(Observer):
    """DashboardObserver for receiving infos about changes of the PetriNet or Scheduling.

    The Observer will send a post request to the dashboard with the data.
    """

    def __init__(self, host: str, scheduler_id: str, pfdl_string: str) -> None:
        self.host: str = host
        self.scheduler_id: str = scheduler_id
        current_timestamp: int = int(round(datetime.timestamp(datetime.now())))
        self.starting_date: int = current_timestamp
        self.pfdl_string: str = pfdl_string
        self.order_finished: bool = False

        threading.Thread(target=send_post_requests, daemon=True).start()

        request_data = {
            "order_id": scheduler_id,
            "starting_date": current_timestamp,
            "last_update": current_timestamp,
            "status": ORDER_STARTED,
            "pfdl_string": self.pfdl_string,
        }

        message_queue.put((self.host + ORDER_ROUTE, request_data))

    def update(self, notification_type: NotificationType, data: Any) -> None:
        if notification_type == NotificationType.PETRI_NET:
            if not self.order_finished:
                content = ""
                with open(
                    PETRI_NET_FILE_LOCATION + self.scheduler_id + "." + PETRI_NET_TYPE
                ) as file:
                    content = file.read()

                request_data = {
                    "order_id": self.scheduler_id,
                    "content": content,
                    "type_pn": PETRI_NET_TYPE,
                }
                message_queue.put((self.host + PETRI_NET_ROUTE, request_data))

        elif notification_type == NotificationType.LOG_EVENT:
            log_event = data[0]
            log_level = data[1]
            order_finished = data[2]

            if order_finished:
                self.order_finished = True

            request_data = {
                "order_id": self.scheduler_id,
                "log_message": log_event,
                "log_date": int(round(datetime.timestamp(datetime.now()))),
                "log_level": log_level,
            }
            message_queue.put((self.host + LOG_EVENT_ROUTE, request_data))

            order_status = ORDER_STARTED
            if order_finished:
                order_status = ORDER_FINISHED

            request_data = {
                "order_id": self.scheduler_id,
                "starting_date": self.starting_date,
                "last_update": int(round(datetime.timestamp(datetime.now()))),
                "status": order_status,
                "pfdl_string": self.pfdl_string,
            }
            message_queue.put((self.host + ORDER_ROUTE, request_data))
