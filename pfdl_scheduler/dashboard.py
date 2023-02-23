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
import argparse
import base64
import requests
from typing import Any
from datetime import datetime
import threading

# local sources
from pfdl_scheduler.api.observer_api import NotificationType
from pfdl_scheduler.api.observer_api import Observer
from pfdl_scheduler.scheduler import Scheduler


def make_post_request(host: str, data: Any):
    requests.post(host, data)


class DashboardObserver(Observer):
    """DashboardObserver for receiving infos about changes of the PetriNet or Scheduling.

    The Observer will send a post request to the dashboard with the data.
    """

    def __init__(self, host: str):
        self.host = host

    def update(self, notification_type: NotificationType, data: Any) -> None:
        if notification_type == NotificationType.PETRI_NET:
            encoded_string = ""
            with open("temp/petri_net.png", "rb") as file:
                encoded_string = base64.b64encode(file.read())

            request_data = {
                "order_id": data,
                "content": b"data:image/png;base64," + encoded_string,
                "format": "png",
            }
            post_thread = threading.Thread(
                target=make_post_request,
                args=[self.host + "/petri_net", request_data],
            )
            post_thread.start()
        elif notification_type == NotificationType.LOG_EVENT:
            scheduler_id = data[0]
            log_event = data[1]
            log_level = data[2]

            request_data = {
                "order_id": scheduler_id,
                "log_message": log_event,
                "log_date": int(round(datetime.timestamp(datetime.now()))),
                "log_level": log_level,
            }

            post_thread = threading.Thread(
                target=make_post_request,
                args=[self.host + "/log_event", request_data],
            )
            post_thread.start()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", type=str, help="the path for the PFDL file.")
    parser.add_argument(
        "-id",
        "--scheduler_id",
        type=str,
        help="associate the scheduler with an id (will be used in the requests).",
    )
    parser.add_argument(
        "-dh", "--dashboard_host", type=str, help="the host address of the PFDL dashboard."
    )

    parser.add_argument(
        "--test_ids",
        action="store_true",
        help="services and tasks get test ids starting from 0.",
    )
    args = parser.parse_args()
    scheduler = Scheduler(pfdl_file_path=args.file_path, scheduler_id=args.scheduler_id)

    if args.dashboard_host:
        dashboard_observer = DashboardObserver(args.dashboard_host)
        scheduler.attach(dashboard_observer)

    scheduler.start()
    while scheduler.running:
        pass


if __name__ == "__main__":
    main()
