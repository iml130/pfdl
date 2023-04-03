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

    def __init__(self, host: str, scheduler_id: str):
        self.host = host
        self.scheduler_id = scheduler_id
        current_timestamp = int(round(datetime.timestamp(datetime.now())))
        self.starting_date = current_timestamp

        threading.Thread(target=send_post_requests, daemon=True).start()

        request_data = {
            "order_id": scheduler_id,
            "starting_date": current_timestamp,
            "last_update": current_timestamp,
            "status": 2,
        }

        message_queue.put((self.host + "/pfdl_order", request_data))

    def update(self, notification_type: NotificationType, data: Any) -> None:
        if notification_type == NotificationType.PETRI_NET:
            content = ""
            with open("temp/petri_net.dot") as file:
                content = file.read()

            request_data = {
                "order_id": self.scheduler_id,
                "content": content,
                "type_pn": "dot",
            }
            message_queue.put((self.host + "/petri_net", request_data))

        elif notification_type == NotificationType.LOG_EVENT:
            log_event = data[0]
            log_level = data[1]
            order_finished = data[2]
            request_data = {
                "order_id": self.scheduler_id,
                "log_message": log_event,
                "log_date": int(round(datetime.timestamp(datetime.now()))),
                "log_level": log_level,
            }
            message_queue.put((self.host + "/log_event", request_data))

            order_status = 2
            if order_finished:
                order_status = 4

            request_data = {
                "order_id": self.scheduler_id,
                "starting_date": self.starting_date,
                "last_update": int(round(datetime.timestamp(datetime.now()))),
                "status": order_status,
            }
            message_queue.put((self.host + "/petri_net", request_data))
